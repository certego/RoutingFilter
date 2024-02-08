import logging
from typing import Optional


class Results:
    def __init__(self, rules, output):
        self.rules = rules
        self.output = output
        self.logger = logging.getLogger(self.__class__.__name__)
