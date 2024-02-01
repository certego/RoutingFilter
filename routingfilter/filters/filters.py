import logging
import re

import macaddress
from IPy import IP
from routingfilter.dictquery import DictQuery


class AbstractFilter:
    def __init__(self, key, value):
        self._key = key if isinstance(key, list) else [key]
        self._value = value if isinstance(value, list) else [value]
        self.logger = logging.getLogger(self.__class__.__name__)

    def match(self, event: DictQuery) -> bool:
        """
        Check if at least a key matches at least one value.

        :param event: event to check
        :type event: DictQuery
        :return: true if event matches, false otherwise
        :rtype: bool
        """
        for key in self._key:
            event_value = event.get(key)
            event_value = event_value if isinstance(event_value, list) else [event_value]
            for value in event_value:
                value = value.lower() if isinstance(value, str) else value
                if value in self._value:
                    return True
        return False


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
        event_keys = [k.lower() for k in event.keys()]
        for key in self._key:
            if key in event_keys:
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
            event_value = event.get(key)
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
            event_value = event.get(key)
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
            if str(value).endswith(suffix):
                return True
        return False


class Keywordfilter(AbstractFilter):
    def match(self, event: DictQuery) -> bool:
        """
        Return True if at least one value is present in the event value of corresponding key.

        :param event: event to filter
        :type event: DictQuery
        :return: true or false
        :rtype: bool
        """
        for key in self._key:
            event_value = event.get(key)
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
            if keyword in value:
                return True
        return False


class RegexpFilter(AbstractFilter):
    def match(self, event: DictQuery) -> bool:
        """
        Return True if at least one regex matches one of the value.

        :param event: event to filter
        :type event: DictQuery
        :return: true or false
        :rtype: bool
        """
        for key in self._key:
            event_value = event.get(key)
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
        value = value.lower()
        for regex in self._value:
            if re.search(regex, value):
                return True
        return False


class NetworkFilter(AbstractFilter):
    def __init__(self, key, value):
        # TODO: check if values are IP?
        super().__init__(key, value)

    def match(self, event: DictQuery) -> bool:
        """
        Return True if at least one event IP address matches one of the value one.

        :param event: event to filter
        :type event: DictQuery
        :return: true or false
        :rtype: bool
        """
        for key in self._key:
            event_value = event.get(key)
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
            for ip in ip_address:
                if ip in IP(self._value):
                    return True
        except ValueError as e:
            self.logger.error(f"Error in parsing IP address (value error): {e}. ")
        except TypeError as e:
            self.logger.error(f"Error in parsing IP address (type error): {e}. ")
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

    def match(self, event: DictQuery) -> bool:
        """
        Return True if the value of the event is equal to or end with one of the value.

        :param event: event to filter
        :type event: DictQuery
        :return: true or false
        :rtype: bool
        """
        for key in self._key:
            event_value = event.get(key)
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
    def __init(self, key, value, comparator_type):
        self._comparator_type = comparator_type
        super().__init__(key, value)

    def match(self, event: DictQuery) -> bool:
        """
        Return True if the key value compared with one of the value is true according to comparator_type.

        :param event: event to filter
        :type event: DictQuery
        :return: true or false
        :rtype: bool
        """
        for key in self._key:
            event_value = event.get(key)
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
                self.logger.error(f"Error in parsing value to float in comparator filter: {e}. ")
                return False
            match self._comparator_type:
                case "GREATER":
                    if value > term:
                        return True
                case "LESS":
                    if value < term:
                        return True
                case "GREATER_EQUAL":
                    if value >= term:
                        return True
                case "LESS_EQUAL":
                    if value <= term:
                        return True


class TypeofFilter(AbstractFilter):
    def __init__(self, key):
        value = ["str", "int", "float", "bool", "list", "dict", "ip", "mac"]
        super().__init__(key, value)

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
                return self._check_type(val_type, event.get(key))

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
            return isinstance(value, str)
        elif val_type == "int":
            return isinstance(value, int)
        elif val_type == "float":
            return isinstance(value, float)
        elif val_type == "bool":
            return isinstance(value, bool)
        elif val_type == "list":
            return isinstance(value, list)
        elif val_type == "dict":
            return isinstance(value, dict)
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
