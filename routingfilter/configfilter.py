import re
import logging

from routingfilter.dictquery import DictQuery
from IPy import IP


class ConfigFilter:

    def __init__(self, filt):
        self.type = str(filt.get('type', '')).upper()
        key = filt.get('key', [])
        value = filt.get('value', [])
        self.key = [key] if isinstance(key, str) else key
        self.value = [value] if isinstance(value, str) or isinstance(value, int) or isinstance(value, float) else value
        self.logger = logging.getLogger(self.__class__.__name__)

    def is_matching(self, data):
        """Return whether the specified event dictionary matches with the loaded filtering rules.

        :param data: The event to by processed
        :type data: dict
        :return: True if the event matches, False otherwise
        :raises: AttributeError if an invalid filter is used (i.e. 'EQUAL' instead of 'EQUALS').
        """
        try:
            self.logger.debug(f"Applying filter {self.type} to event: {data}")
            return getattr(self, '_filter_{}'.format(self.type))(data)
        except AttributeError:
            self.logger.error(f"Invalid filter specified in rules: {self.type}")
            raise

    def _filter_ALL(self, data):
        return True

    def _filter_EXISTS(self, data):
        for key in self.key:
            if DictQuery(data).get(key) is not None:
                return True
        return False

    def _filter_NOT_EXISTS(self, data):
        for key in self.key:
            if DictQuery(data).get(key) is not None:
                return False
        return True

    def _filter_EQUALS(self, data):
        for key in self.key:
            target = str(DictQuery(data).get(key, ''))
            if isinstance(target, list):
                for t in target:
                    if self.__check_equals(t):
                        return True
            else:
                if self.__check_equals(target):
                    return True
        return False

    def __check_equals(self, target):
        target = target.lower()
        for value in self.value:
            if str(value).lower() == target:
                return True
        return False

    def _filter_STARTSWITH(self, data):
        for key in self.key:
            target = str(DictQuery(data).get(key, ''))
            if isinstance(target, list):
                for t in target:
                    if self.__check_startswith(t):
                        return True
            else:
                if self.__check_startswith(target):
                    return True
        return False

    def __check_startswith(self, target):
        target = target.lower()
        for value in self.value:
            if target.startswith(str(value).lower()):
                return True
        return False

    def _filter_KEYWORD(self, data):
        for key in self.key:
            target = str(DictQuery(data).get(key, ''))
            if isinstance(target, list):
                for t in target:
                    if self.__check_keyword(t):
                        return True
            else:
                if self.__check_keyword(target):
                    return True
        return False

    def __check_keyword(self, target):
        target = target.lower()
        for value in self.value:
            if str(value).lower() in target:
                return True
        return False

    def _filter_REGEXP(self, data):
        for key in self.key:
            target = str(DictQuery(data).get(key, ''))
            if isinstance(target, list):
                for t in target:
                    if self.__check_regexp(t):
                        return True
            else:
                if self.__check_regexp(target):
                    return True
        return False

    def __check_regexp(self, target):
        for value in self.value:
            if re.search(value, target, re.I | re.M):
                return True
        return False

    def _filter_NETWORK(self, data):
        for key in self.key:
            target = DictQuery(data).get(key, '0.0.0.0')
            if isinstance(target, list):
                for t in target:
                    if self.__check_network(t):
                        return True
            else:
                if self.__check_network(target):
                    return True
        return False

    def __check_network(self, target):
        for value in self.value:
            try:
                if target in IP(value):
                    return True
            except ValueError:
                raise ValueError(f"Invalid IP address: {value}")
        return False

    def _filter_NOT_NETWORK(self, data):
        for key in self.key:
            target = DictQuery(data).get(key, '0.0.0.0')
            if isinstance(target, list):
                for t in target:
                    # Se fa match anche solo un IP allora ritorno False
                    if not self.__check_not_network(t):
                        return False
            else:
                if not self.__check_not_network(target):
                    return False
        return True

    def __check_not_network(self, target):
        for value in self.value:
            if target in IP(value):
                return False
        return True

    def _filter_DOMAIN(self, data):
        for key in self.key:
            target = str(DictQuery(data).get(key, ''))
            if isinstance(target, list):
                for t in target:
                    if self.__check_domain(t):
                        return True
            else:
                if self.__check_domain(target):
                    return True
        return False

    def __check_domain(self, target):
        target = target.lower()
        for value in self.value:
            value = str(value).lower()
            if target == value or target.endswith('.' + value):
                return True
        return False

    def _filter_GREATER(self, data):
        return self.__number_comparator(data, self.__check_greater)

    def _filter_LESS(self, data):
        return self.__number_comparator(data, self.__check_less)

    def _filter_GREATER_EQ(self, data):
        return self.__number_comparator(data, self.__check_greater_eq)

    def _filter_LESS_EQ(self, data):
        return self.__number_comparator(data, self.__check_less_eq)

    def __number_comparator(self, data, comparator):
        # Wrapper for filters GREATER, LESS, GREATER_EQ, LESS_EQ
        for key in self.key:
            target = str(DictQuery(data).get(key, ''))
            if not target:
                return False
            if isinstance(target, list):
                for t in target:
                    try:
                        if comparator(float(t)):
                            return True
                    except ValueError:
                        raise ValueError(f"Invalid target in GREATER filter: {t} is not integer")
            else:
                try:
                    if comparator(float(target)):
                        return True
                except ValueError:
                    raise ValueError(f"Invalid target in GREATER filter: {target} is not integer")
        return False

    def __check_greater(self, target):
        for value in self.value:
            if target > float(value):
                return True
        return False

    def __check_less(self, target):
        for value in self.value:
            if target < float(value):
                return True
        return False

    def __check_greater_eq(self, target):
        for value in self.value:
            if target >= float(value):
                return True
        return False

    def __check_less_eq(self, target):
        for value in self.value:
            if target <= float(value):
                return True
        return False
