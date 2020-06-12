import re

from routingfilter.dictquery import DictQuery
from IPy import IP


class ConfigFilter:

    def __init__(self, filt):
        self.type = str(filt.get('type', '')).upper()
        key = filt.get('key', [])
        value = filt.get('value', [])
        self.key = [key] if isinstance(key, str) else key
        self.value = [value] if isinstance(value, str) else value

    def is_matching(self, data):
        try:
            return getattr(self, '_filter_{}'.format(self.type))(data)
        except AttributeError:
            return False

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
                    if self._check_equals(t):
                        return True
            else:
                if self._check_equals(target):
                    return True
        return False

    def _check_equals(self, target):
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
                    if self._check_startswith(t):
                        return True
            else:
                if self._check_startswith(target):
                    return True
        return False

    def _check_startswith(self, target):
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
                    if self._check_keyword(t):
                        return True
            else:
                if self._check_keyword(target):
                    return True
        return False

    def _check_keyword(self, target):
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
                    if self._check_regexp(t):
                        return True
            else:
                if self._check_regexp(target):
                    return True
        return False

    def _check_regexp(self, target):
        for value in self.value:
            if re.search(value, target, re.I | re.M):
                return True
        return False

    def _filter_NETWORK(self, data):
        for key in self.key:
            target = DictQuery(data).get(key, '0.0.0.0')
            if isinstance(target, list):
                for t in target:
                    if self._check_network(t):
                        return True
            else:
                if self._check_network(target):
                    return True
        return False

    def _check_network(self, target):
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
                    if not self._check_not_network(t):
                        return False
            else:
                if not self._check_not_network(target):
                    return False
        return True

    def _check_not_network(self, target):
        for value in self.value:
            if target in IP(value):
                return False
        return True

    def _filter_DOMAIN(self, data):
        for key in self.key:
            target = str(DictQuery(data).get(key, ''))
            if isinstance(target, list):
                for t in target:
                    if self._check_domain(t):
                        return True
            else:
                if self._check_domain(target):
                    return True
        return False

    def _check_domain(self, target):
        target = target.lower()
        for value in self.value:
            value = str(value).lower()
            if target == value or target.endswith('.' + value):
                return True
        return False
