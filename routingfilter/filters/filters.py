import logging
import re
from abc import ABC, abstractmethod
from typing import Optional

import macaddress
from IPy import IP
from routingfilter.dictquery import DictQuery


class AbstractFilter(ABC):
    def __init__(self, key, value, **kwargs):
        self._key = key if isinstance(key, list) else [key]
        self._value = value if isinstance(value, list) else [value]
        self.logger = logging.getLogger(self.__class__.__name__)
        self._check_value()

    @abstractmethod
    def match(self, event: DictQuery) -> bool:
        return NotImplemented

    def _check_value(self) -> Optional[Exception]:
        """
        Check if values in self._value are correct and raise an exception if they are incorrect.

        :return: no value or raise an exception
        :rtype: Optional[Exception]
        """
        return None


class AllFilter(AbstractFilter):
    def __init__(self):
        key = value = []
        super().__init__(key, value)

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

    def match(self, event: DictQuery):
        """
        Check if at least a key matches at least one value.

        :param event: event to check
        :type event: DictQuery
        :return: true if event matches, false otherwise
        :rtype: bool
        """
        filter_value = []
        for value in self._value:
            value = value.lower() if isinstance(value, str) else str(value)
            filter_value.append(value)
        for key in self._key:
            event_value = event.get(key, [])
            event_value = event_value if isinstance(event_value, list) else [event_value]
            for value in event_value:
                value = value.lower() if isinstance(value, str) else str(value)
                if value in filter_value:
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
                return self._check_startswith(str(value))

    def _check_startswith(self, value: str) -> bool:
        """
        Check if the value starts with one of the prefix given.

        :param value: value to check
        :type value: str
        :return: true or false
        :rtype: bool
        """
        value = value.lower()
        for prefix in self._value:
            prefix = str(prefix).lower()
            if value.startswith(prefix):
                return True
        return False


class EndswithFilter(AbstractFilter):
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
                return self._check_endswith(str(value))

    def _check_endswith(self, value):
        """
        Check if the value end with one of the suffix given.

        :param value: value to check
        :type value: str
        :return: true or false
        :rtype: bool
        """
        value = value.lower()
        for suffix in self._value:
            suffix = str(suffix).lower()
            if str(value).endswith(suffix):
                return True
        return False


class KeywordFilter(AbstractFilter):
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
                return self._check_keyword(str(value))

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
            keyword = str(keyword).lower()
            if keyword in value:
                return True
        return False


class RegexpFilter(AbstractFilter):
    def _check_value(self) -> Optional[Exception]:
        """
        Check if values in self._value are valid regexes.

        :return: none or error generated:
        :rtype: Optional[Exception]
        """
        for value in self._value:
            try:
                re.compile(value)
            except re.error as e:
                self.logger.error(f"Invalid regex {value}, during check of value list {self._value}. Error message: {e}")
                raise ValueError(f"Regex check failed: error for value {value}. Error message: {e}")
        return None

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
                return self._check_regex(str(value))

    def _check_regex(self, value: str) -> bool:
        """
        Check if at least one regex matches the value.

        :param value: value to check
        :type value: str
        :return: true or false
        :rtype: bool
        """
        for regex in self._value:
            if re.search(regex, value):
                return True
        return False


class NetworkFilter(AbstractFilter):
    def __init__(self, key, value):
        super().__init__(key, value)

    def _check_value(self) -> Optional[Exception]:
        """
        Check if the values in self._value are valid IP addresses.

        :return: none or error generated
        :rtype: Optional[Exception]
        """
        for value in self._value:
            try:
                value = IP(value)
            except ValueError as e:
                self.logger.error(f"IP address (value error) error, during check of value {value} in list {self._value}. Error was: {e}.")
                raise ValueError(f"IP address check failed: value error for value {value}.")
            except TypeError as e:
                self.logger.error(f"IP address (type error) error, during check of value {value} in list {self._value}. Error was: {e}.")
                raise ValueError(f"IP address check failed: type error for value {value}.")
        return None

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
                return self._check_network(str(ip_address))

    def _check_network(self, ip_address: str) -> bool:
        """
        Check if IP address matches one of the value. If it is not valid IP address, return False.

        :param ip_address: IP address to check
        :type ip_address: str
        :return: true or false
        :rtype: bool
        """
        try:
            ip_address = IP(ip_address)
            for value in self._value:
                if ip_address in IP(value):
                    return True
        except ValueError as e:
            self.logger.debug(f"Error in parsing IP address (value error): {e}. ")
        except TypeError as e:
            self.logger.debug(f"Error in parsing IP address (type error): {e}. ")
        return False


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

    def _check_value(self) -> Optional[Exception]:
        """
        Check if values in self._value are string.

        :return: none or error generated
        :rtype: bool
        """
        for value in self._value:
            if not isinstance(value, str):
                raise ValueError(f"Domain check failed: value {value} is not a string.")
        return None

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
                return self._check_domain(str(value))

    def _check_domain(self, value: str) -> bool:
        """
        Check if value is equal to or ends with one of domains.

        :param value: value to check
        :type value: str
        :return:
        """
        value = value.lower()
        for domain in self._value:
            domain = str(domain).lower()
            if value == domain or str(value).endswith(f".{domain}"):
                return True
        return False


class ComparatorFilter(AbstractFilter):
    def __init__(self, key, value, comparator_type):
        self._comparator_type = comparator_type
        self._check_comparator_type()
        super().__init__(key, value)

    def _check_value(self) -> Optional[Exception]:
        """
        Check if values in self._value are float.

        :return: none or error generated
        :rtype: Optional[Exception]
        """
        for value in self._value:
            try:
                float(value)
            except ValueError:
                self.logger.error(f"Comparator check failed: value {value} of list {self._value} is not a float")
                raise ValueError(f"Comparator check failed: value {value} is not a float")
        return None

    def _check_comparator_type(self) -> Optional[Exception]:
        """
        Check if comparator is valid.

        :return: none or error generated
        :rtype: Optional[Exception]
        """
        if self._comparator_type not in ["GREATER", "LESS", "GREATER_EQ", "LESS_EQ"]:
            self.logger.error(f"Comparator check failed: value {self._comparator_type} is not valid.")
            raise ValueError(f"Comparator type check failed. {self._comparator_type} is not a valid comparator.")
        return None

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
                return self._compare(value)

    def _compare(self, value: float) -> bool:
        """
        Compare value to term in _value.

        :param value: value to compare
        :type value: float
        :return: true or false
        :rtype: bool
        """
        for term in self._value:
            try:
                term = float(term)
                value = float(value)
            except ValueError as e:
                self.logger.debug(f"Error in parsing value to float in comparator filter: {e}. ")
                return False
            match self._comparator_type:
                case "GREATER":
                    if value > term:
                        return True
                case "LESS":
                    if value < term:
                        return True
                case "GREATER_EQ":
                    if value >= term:
                        return True
                case "LESS_EQ":
                    if value <= term:
                        return True
        return False


class TypeofFilter(AbstractFilter):
    def __init__(self, key, value):
        super().__init__(key, value)

    def _check_value(self) -> Optional[Exception]:
        """
        Check if value is a correct type.

        :return: no value or raised an exception
        :rtype: Optional[Exception]
        """
        valid_type = ["str", "int", "float", "bool", "list", "dict", "ip", "mac"]
        for value in self._value:
            if value not in valid_type:
                self.logger.error(f"Type check failed: value {value} of list {self._value} is invalid.")
                raise ValueError(f"Type check failed: value {value} is invalid.")
        return None

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
                if self._check_type(event.get(key), val_type):
                    return True
        return False

    def _check_type(self, value: any, val_type: str) -> bool:
        """
        Check type of the value.

        :param value: value to check
        :type value: any
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
            return self._check_ip(value)
        elif val_type == "mac":
            return self._check_mac(value)
        return False

    def _check_ip(self, value: any) -> bool:
        """
        Check if value is IP address.

        :param value: value to check
        :type: any
        :return: true or false
        :rtype: bool
        """
        try:
            if isinstance(value, int) or int(value):
                return False
        except ValueError:
            try:
                IP(value)
                return True
            except ValueError:
                return False
            except TypeError:
                return False

    def _check_mac(self, value: any) -> bool:
        """
        Check if value is a MAC address.

        :param value: value to check
        :type value: any
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
