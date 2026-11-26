import functools
import ipaddress
import logging
import math
import re
from abc import ABC, abstractmethod
from bisect import bisect_right
from typing import Any

import macaddress
from routingfilter.dictquery import DictQuery


@functools.lru_cache(maxsize=4096)
def _parse_network(text: str) -> tuple[int, int, int] | None:
    """Parse a string into (IP version, first address, last address) as integers, or None if it is not a valid network. Cached, including the failures."""
    try:
        network = ipaddress.ip_network(text)
    except (ValueError, TypeError):
        return None
    return network.version, int(network.network_address), int(network.broadcast_address)


class AbstractFilter(ABC):
    def __init__(self, key, value, **kwargs):
        self._key = key if isinstance(key, list) else [key]
        self._value = value if isinstance(value, list) else [value]
        self.logger = logging.getLogger(self.__class__.__name__)
        self._check_value()

    @abstractmethod
    def match(self, event: DictQuery) -> bool:
        return NotImplemented

    @abstractmethod
    def _check_value(self) -> None:
        """
        Check if values in self._value are correct and raise an exception if they are incorrect. If necessary, it converts value in lower case.

        :return: no value or raise an exception
        :rtype: None
        :raises Exception: if the value is not correct
        """
        return NotImplemented


class AllFilter(AbstractFilter):
    def __init__(self):
        key = value = []
        super().__init__(key, value)

    def _check_value(self) -> None:
        return

    def match(self, event: DictQuery) -> bool:
        """
        Return always true.

        :param event: event to check
        :type event: DictQuery
        :return: always true
        :rtype: bool
        """
        return True


class ExistFilter(AbstractFilter):
    def __init__(self, key):
        value = []
        super().__init__(key, value)

    def _check_value(self) -> None:
        return

    def match(self, event: DictQuery) -> bool:
        """
        Return True if one of the key exists in the event.

        :param event: event to check
        :type event: DictQuery
        :return: true if a key exists, false otherwise
        :rtype: bool
        """
        for key in self._key:
            if event.get(key) is not None:
                return True
        return False


class NotExistFilter(ExistFilter):
    def match(self, event: DictQuery) -> bool:
        """
        Return True if no key exists in the event.

        :param event: event to check
        :type event: DictQuery
        :return: true if no key exists, false otherwise
        :rtype: bool
        """
        return not ExistFilter.match(self, event)


class EqualFilter(AbstractFilter):
    def __init__(self, key, value):
        super().__init__(key, value)

    def _check_value(self) -> None:
        self._value = [str(value).lower() for value in self._value]
        self._value_set = frozenset(self._value)

    def match(self, event: DictQuery):
        """
        Check if at least a key matches at least one value.

        :param event: event to check
        :type event: DictQuery
        :return: true if event matches, false otherwise
        :rtype: bool
        """
        for key in self._key:
            event_value = event.get(key, [])
            event_value = event_value if isinstance(event_value, list) else [event_value]
            for value in event_value:
                if str(value).lower() in self._value_set:
                    return True
        return False


class NotEqualFilter(EqualFilter):
    def match(self, event: DictQuery) -> bool:
        """
        Return True if no value is equal to ones corresponding to the event keys.

        :param event: event to filter
        :type event: DictQuery
        :return: true or false
        :rtype: bool
        """
        return not EqualFilter.match(self, event)


class StartswithFilter(AbstractFilter):
    def _check_value(self) -> None:
        self._value = [str(prefix).lower() for prefix in self._value]
        self._prefixes = tuple(self._value)

    def match(self, event: DictQuery) -> bool:
        """
        Return True if at least one event value corresponding to a key starts with one of the value.

        :param event: event to filter
        :type event: DictQuery
        :return: true or false
        :rtype: bool
        """
        for key in self._key:
            event_value = event.get(key, [])
            event_value = event_value if isinstance(event_value, list) else [event_value]
            for value in event_value:
                if self._check_startswith(str(value)):
                    return True
        return False

    def _check_startswith(self, value: str) -> bool:
        """
        Check if the value starts with one of the prefix given.

        :param value: value to check
        :type value: str
        :return: true or false
        :rtype: bool
        """
        return value.lower().startswith(self._prefixes)


class EndswithFilter(AbstractFilter):
    def _check_value(self) -> None:
        self._value = [str(suffix).lower() for suffix in self._value]
        self._suffixes = tuple(self._value)

    def match(self, event: DictQuery) -> bool:
        """
        Return True if at least one event value corresponding to a key ends with one of the value.

        :param event: event to filter
        :type event: DictQuery
        :return: true or false
        :rtype: bool
        """
        for key in self._key:
            event_value = event.get(key, [])
            event_value = event_value if isinstance(event_value, list) else [event_value]
            for value in event_value:
                if self._check_endswith(str(value)):
                    return True
        return False

    def _check_endswith(self, value: str) -> bool:
        """
        Check if the value end with one of the suffix given.

        :param value: value to check
        :type value: str
        :return: true or false
        :rtype: bool
        """
        return value.lower().endswith(self._suffixes)


class KeywordFilter(AbstractFilter):
    def _check_value(self) -> None:
        self._value = [str(keyword).lower() for keyword in self._value]

    def match(self, event: DictQuery) -> bool:
        """
        Return True if at least one value is present in the event value of corresponding key.

        :param event: event to filter
        :type event: DictQuery
        :return: true or false
        :rtype: bool
        """
        for key in self._key:
            event_value = event.get(key, [])
            event_value = event_value if isinstance(event_value, list) else [event_value]
            for value in event_value:
                if self._check_keyword(str(value)):
                    return True
        return False

    def _check_keyword(self, value: str) -> bool:
        """
        Check if keyword is contained in value.

        :param value: value to check
        :type value: str
        :return: true or false
        :rtype: bool
        """
        value = value.lower()
        for keyword in self._value:
            if keyword in value:
                return True
        return False


class RegexpFilter(AbstractFilter):
    def _check_value(self) -> None:
        """
        Check if values in self._value are valid regexes.

        :return: none or error generated:
        :rtype: None
        :raises ValueError: regex check failed
        """
        tmp = []
        for value in self._value:
            try:
                tmp.append(re.compile(value))
            except re.error as e:
                self.logger.error(f"Invalid regex {value}, during check of value list {self._value}. Error message: {e}")
                raise ValueError(f"Regex check failed: error for value {value}. Error message: {e}")
        self._value = tmp

    def match(self, event: DictQuery) -> bool:
        """
        Return True if at least one regex matches one of the value.

        :param event: event to filter
        :type event: DictQuery
        :return: true or false
        :rtype: bool
        """
        for key in self._key:
            event_value = event.get(key, [])
            event_value = event_value if isinstance(event_value, list) else [event_value]
            for value in event_value:
                if self._check_regex(str(value)):
                    return True
        return False

    def _check_regex(self, value: str) -> bool:
        """
        Check if at least one regex matches the value.

        :param value: value to check
        :type value: str
        :return: true or false
        :rtype: bool
        """
        for regex in self._value:
            if regex.search(value):
                return True
        return False


class NetworkFilter(AbstractFilter):
    def __init__(self, key, value):
        super().__init__(key, value)

    def _check_value(self) -> None:
        """
        Check if the values in self._value are valid IP addresses.

        :return: none or error generated
        :rtype: None
        :raises ValueError: IP address parsing failed
        """
        tmp = []
        for value in self._value:
            try:
                network = ipaddress.ip_network(value)
            except ValueError as e:
                self.logger.error(f"IP address (value error) error, during check of value {value} in list {self._value}. Error was: {e}.")
                raise ValueError(f"IP address check failed: value error for value {value}.")
            except TypeError as e:
                self.logger.error(f"IP address (type error) error, during check of value {value} in list {self._value}. Error was: {e}.")
                raise ValueError(f"IP address check failed: type error for value {value}.")
            else:
                tmp.append(network)
        self._value = tmp
        self._starts = {4: [], 6: []}
        self._ends = {4: [], 6: []}
        # CIDR blocks are either nested or disjoint: keeping only the outermost ones leaves sorted disjoint intervals
        for network in sorted(self._value, key=lambda n: (n.version, int(n.network_address), n.prefixlen)):
            start, end = int(network.network_address), int(network.broadcast_address)
            ends = self._ends[network.version]
            if ends and start <= ends[-1]:
                continue
            self._starts[network.version].append(start)
            ends.append(end)

    def match(self, event: DictQuery) -> bool:
        """
        Return True if at least one event IP address matches one of the value one.

        :param event: event to filter
        :type event: DictQuery
        :return: true or false
        :rtype: bool
        """
        for key in self._key:
            event_value = event.get(key, [])
            event_value = event_value if isinstance(event_value, list) else [event_value]
            for ip_address in event_value:
                if self._check_network(str(ip_address)):
                    return True
        return False

    def _check_network(self, ip_address: str) -> bool:
        """
        Check if IP address matches one of the value. If it is not valid IP address, return False.

        :param ip_address: IP address to check
        :type ip_address: str
        :return: true or false
        :rtype: bool
        """
        parsed = _parse_network(ip_address)
        if parsed is None:
            self.logger.debug(f"Error in parsing IP address: {ip_address!r} is not a valid network. ")
            return False
        version, start, end = parsed
        index = bisect_right(self._starts[version], start) - 1
        return index >= 0 and end <= self._ends[version][index]


class NotNetworkFilter(NetworkFilter):
    def match(self, event: DictQuery) -> bool:
        """
        Return True if at least no event IP address matches the value one.

        :param event: event to filter
        :type event: DictQuery
        :return: true or false
        :rtype: bool
        """
        return not NetworkFilter.match(self, event)


class DomainFilter(AbstractFilter):
    def __init__(self, key, value):
        super().__init__(key, value)

    def _check_value(self) -> None:
        """
        Check if values in self._value are string.

        :return: none or error generated
        :rtype: bool
        """
        tmp = []
        for domain in self._value:
            if not isinstance(domain, str):
                raise ValueError(f"Domain check failed: value {domain} is not a string.")
            tmp.append(domain.lower())
        self._value = tmp
        self._domains = frozenset(self._value)
        self._dot_suffixes = tuple(f".{domain}" for domain in self._value)

    def match(self, event: DictQuery) -> bool:
        """
        Return True if the value of the event is equal to or end with one of the value.

        :param event: event to filter
        :type event: DictQuery
        :return: true or false
        :rtype: bool
        """
        for key in self._key:
            event_value = event.get(key, [])
            event_value = event_value if isinstance(event_value, list) else [event_value]
            for value in event_value:
                if self._check_domain(str(value)):
                    return True
        return False

    def _check_domain(self, value: str) -> bool:
        """
        Check if value is equal to or ends with one of domains.

        :param value: value to check
        :type value: str
        :return:
        """
        value = value.lower()
        return value in self._domains or value.endswith(self._dot_suffixes)


class ComparatorFilter(AbstractFilter):
    def __init__(self, key, value, comparator_type):
        self._comparator_type = comparator_type
        self._check_comparator_type()
        super().__init__(key, value)

    def _check_value(self) -> None:
        """
        Check if values in self._value are float.

        :return: none or error generated
        :rtype: None
        """
        tmp = []
        for value in self._value:
            try:
                tmp.append(float(value))
            except (TypeError, ValueError):
                self.logger.error(f"Comparator check failed: value {value} of list {self._value} is not a float")
                raise ValueError(f"Comparator check failed: value {value} is not a float")
        self._value = tmp
        # A NaN term never matches, and min()/max() would return NaN depending on its position
        terms = [term for term in self._value if not math.isnan(term)]
        if not terms:
            self._threshold = None
        elif self._comparator_type in ("GREATER", "GREATER_EQ"):
            self._threshold = min(terms)
        else:
            self._threshold = max(terms)

    def _check_comparator_type(self) -> None:
        """
        Check if comparator is valid.

        :return: none or error generated
        :rtype: None
        """
        if self._comparator_type not in ["GREATER", "LESS", "GREATER_EQ", "LESS_EQ"]:
            self.logger.error(f"Comparator check failed: value {self._comparator_type} is not valid.")
            raise ValueError(f"Comparator type check failed. {self._comparator_type} is not a valid comparator.")

    def match(self, event: DictQuery) -> bool:
        """
        Return True if the key value compared with one of the value is true according to comparator_type.

        :param event: event to filter
        :type event: DictQuery
        :return: true or false
        :rtype: bool
        """
        for key in self._key:
            event_value = event.get(key, [])
            event_value = event_value if isinstance(event_value, list) else [event_value]
            for value in event_value:
                if self._compare(value):
                    return True
        return False

    def _compare(self, value: Any) -> bool:
        """
        Compare value to the threshold derived from _value. If the value cannot be converted to float (e.g. the event field is missing
        and the key resolves to a dict or to None), return False. An int too large for a float is compared as +/-infinity.

        :param value: value to compare
        :type value: Any
        :return: true or false
        :rtype: bool
        """
        try:
            value = float(value)
        except OverflowError:
            value = math.inf if value > 0 else -math.inf
        except (TypeError, ValueError) as e:
            self.logger.debug(f"Error in parsing value to float in comparator filter: {e}. ")
            return False
        if self._threshold is None:
            return False
        match self._comparator_type:
            case "GREATER":
                return value > self._threshold
            case "LESS":
                return value < self._threshold
            case "GREATER_EQ":
                return value >= self._threshold
            case "LESS_EQ":
                return value <= self._threshold
        return False


class TypeofFilter(AbstractFilter):
    def __init__(self, key, value):
        super().__init__(key, value)

    def _check_value(self) -> None:
        """
        Check if value is a correct type.

        :return: no value or raised an exception
        :rtype: None
        """
        valid_type = ["str", "int", "float", "bool", "list", "dict", "ip", "mac"]
        tmp = []
        for value in self._value:
            value = str(value).lower()
            if value not in valid_type:
                self.logger.error(f"Type check failed: value {value} of list {self._value} is invalid.")
                raise ValueError(f"Type check failed: value {value} is invalid.")
            tmp.append(value)
        self._value = tmp

    def match(self, event: DictQuery) -> bool:
        """
        Return True if the value type of the key matches one of the values.

        :param event: event to filter
        :type event DictQuery
        :return: true or false
        :rtype: bool
        """

        for key in self._key:
            for val_type in self._value:
                if TypeofFilter._check_type(event.get(key), val_type):
                    return True
        return False

    @staticmethod
    def _check_type(value: str | int | float | list | dict, val_type: str) -> bool:
        """
        Check type of the value.

        :param value: value to check
        :type value: str | int | float | list | dict
        :param val_type: type
        :rtype str
        :return: true or false
        :rtype: bool
        """
        if val_type == "str":
            return type(value) is str
        elif val_type == "int":
            return type(value) is int
        elif val_type == "float":
            return type(value) is float
        elif val_type == "bool":
            return type(value) is bool
        elif val_type == "list":
            return type(value) is list
        elif val_type == "dict":
            return type(value) is dict
        elif val_type == "ip":
            return TypeofFilter._check_ip(value)
        elif val_type == "mac":
            return TypeofFilter._check_mac(value)
        return False

    @staticmethod
    def _check_ip(value: Any) -> bool:
        """
        Check if value is IP address. Values which are neither numbers nor IP addresses (e.g. a missing event field
        resolving to None or to a dict) are not IP addresses, so False is returned.

        :param value: value to check
        :type: Any
        :return: true or false
        :rtype: bool
        """
        try:
            if isinstance(value, int) or int(value):
                return False
        except (ValueError, TypeError):
            try:
                ipaddress.ip_address(value)
            except (ValueError, TypeError):
                return False
            else:
                return True
        return False

    @staticmethod
    def _check_mac(value: Any) -> bool:
        """
        Check if value is a MAC address.

        :param value: value to check
        :type value: Any
        :return: true or false
        :rtype: bool
        """
        if isinstance(value, int):
            return False
        try:
            macaddress.EUI48(value)
            return True
        except ValueError:
            return False
        except TypeError:
            return False
