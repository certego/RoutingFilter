import copy
import logging
from datetime import datetime
from typing import List

from routingfilter.dictquery import DictQuery

from .filters import AbstractFilter
from .results import Results


class Rule:
    def __init__(self, uid, output):
        self.uid = uid
        self.output = DictQuery(output) if output else None
        self._stats = {}
        self._filters = []
        self.logger = logging.getLogger(self.__class__.__name__)

    def match(self, event: DictQuery) -> Results | None:
        """
        Call match method for each filter. If all filters match, the output is returned, None otherwise. If the filter
        matches, the output key with current timestamp in ISO format is added to certego.routing_history field of the event.
        The match is added also to stats. If "certego.routing_history" already contains the output key value, the filter must not match and None is returned.

        :param event: event to check
        :type event: DictQuery
        :return: the output or no value
        :rtype: Results | None
        """
        for f in self._filters:
            if not f.match(event):
                return None
        now = datetime.now().isoformat()
        # check if output keys are in certego.routing_history keys
        if self.output and set(self.output.keys()) <= set(event.get("certego.routing_history").keys()):
            return None
        # add stats
        event_id = event.get("rule.name", "unknown")
        self._add_stats(event_id)
        # if output is None
        if not self.output:
            return Results(rules=self.uid, output=None)
        # if at least one output key is not in certego.routing_history keys, it is added to certego.routing_history keys and delete from output keys
        output_copy = copy.deepcopy(self.output)
        for key in self.output.keys():
            routing_history = event.get("certego.routing_history")
            if key in routing_history:
                output_copy.pop(key)
            else:
                routing_history.update({key: now})
        results = Results(rules=self.uid, output=output_copy)
        return results

    def _add_stats(self, event_id: str) -> None:
        """
        Add to stats a new entry with event_id and number of hits or increment it if the entry already exists.

        :param event_id: id of the event which stats are to add or update
        :type event_id: str
        :return: no value
        :rtype: None
        """
        if event_id in self._stats.keys():
            self._stats[event_id] += 1
        else:
            self._stats.update({event_id: 1})

    def get_stats(self, delete=False) -> dict:
        """
        Retrieve all stats in format {uid: stats}. If "delete" is set to true, it returns stats and then deletes all.

        :param delete: if true delete stats
        :type delete: bool
        :return: all stats
        :rtype: dict
        """
        stats = {str(self.uid): self._stats}
        if delete:
            self._stats = {}
        return stats

    def add_filter(self, filters: AbstractFilter | List[AbstractFilter]) -> None:
        """
        Add a filter or a list of filters to the rule.

        :param filters: list of filters to add to the rule
        :type filters: AbstractFilter | List[AbstractFilter]
        :return: no value
        :rtype: None
        """
        if not isinstance(filters, list):
            filters = [filters]
        self._filters += filters


class RuleManager:
    def __init__(self, tag: str):
        self.tag = tag
        self._rules = []
        self.logger = logging.getLogger(self.__class__.__name__)

    def count(self) -> int:
        """
        Return the number of rules.

        :return: number of rules
        :rtype: int
        """
        return len(self._rules)

    def match(self, event: DictQuery, tag: str) -> Results | None:
        """
        Call all match methods of the Rules and return the result of first match.
        Return None if no match is found or tag is different from the one in tag attribute.

        :param event: event to check
        :type event: DictQuery
        :param tag: routing tag
        :type tag: str
        :return: result of match or None
        :rtype: Results | None
        """
        if tag != self.tag:
            return None
        for rule in self._rules:
            match_rule = rule.match(event)
            if match_rule:
                return match_rule
        return None

    def add_rule(self, rule: Rule | List[Rule]) -> None:
        """
        Add rule or a list of rule to rule list so that sorting by "group_number" and "rule_number" is maintained.

        :param rule: rule or rule list to add
        :type rule: Rule | List[Rule]
        :return: no value
        :rtype: None
        """
        if not isinstance(rule, list):
            rule = [rule]
        for r in rule:
            self._rules.append(r)

    def get_stats(self, delete=False) -> dict:
        """
        Call get_stats methods of the rules and return a dictionary with all results.

        :param delete: if true delete each stat
        :type delete: bool
        :return: stats dictionary
        :rtype: dict
        """
        stats = {}
        for rule in self._rules:
            stats.update(rule.get_stats(delete))
        return stats
