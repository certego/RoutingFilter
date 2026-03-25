import logging
from typing import List, Optional

from routingfilter.dictquery import DictQuery

from .results import Results
from .rule import RuleManager


class Stream:
    def __init__(self, stream):
        self.stream = stream
        self._ruleManagers = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def count(self) -> int:
        """
        Returns the number of rules in the stream.

        :return: number of rules
        :rtype: int
        """
        count_rules = 0
        for key in self._ruleManagers.keys():
            count_rules += self._ruleManagers[key].count()
        return count_rules

    def match(self, event: DictQuery, tag_field_name: str) -> List[Results]:
        """
        Call all ruleManagers that contain tha tag of event "tags" field (that could be a list).
        It returns a list of dictionaries representing eventual matches or None if no matches are found.
        If a RuleManager has the tag "all", match method must be called before any. If there is a match, it returns
        immediately the result without check RuleManager for other tag.

        :param event: event to check
        :type event: DictQuery
        :param tag_field_name: the event field to search into (default "tags")
        :type tag_field_name: str
        :return: list of matches or None otherwise
        :rtype: List[Results]
        """
        match_list = []
        tags = event.get(tag_field_name, [])
        if not isinstance(tags, list):
            tags = [tags]
        # avoid duplicates
        tags = set(tags)

        # tag all
        if "all" in self._ruleManagers.keys():
            all_match = self._ruleManagers["all"].match(event, "all")
            if all_match is not None:
                return [all_match]
        for tag in tags:
            # append Results object or None
            if tag in self._ruleManagers.keys():
                match = self._ruleManagers[tag].match(event, tag)
                if match:
                    match_list.append(match)
        return match_list

    def add_rulemanager(self, rulemanager: RuleManager | List[RuleManager]) -> None:
        """
        Add one or more Rule Manager to rule manager dictionary. If there is already a Rule Manager for the same tag, error is generated.

        :param rulemanager: one or more rule manager to add
        :type rulemanager: RuleManager | List[RuleManager]
        :return: no value or error generated
        :rtype: Optional[Exception]
        """
        if not isinstance(rulemanager, list):
            rulemanager = [rulemanager]
        for rm in rulemanager:
            tag = rm.tag
            # if Rule manager already exists error is generated
            if tag in self._ruleManagers and self._ruleManagers[tag] == rm:
                raise ValueError(f"Rule Manager {rm} already exists for tag {tag}.")
            self._ruleManagers.update({tag: rm})

    def delete_rulemanager(self, tags: str | List[str]) -> None:
        """
        Delete all Rule Manager with tags given.

        :param tags: rule manager tags to delete
        :type tags: str | List[str]
        :return: no value
        :rtype: None
        """
        if not isinstance(tags, list):
            tags = [tags]
        for tag in tags:
            if tag in self._ruleManagers.keys():
                self._ruleManagers.pop(tag)

    def get_stats(self, delete=False) -> dict:
        """
        Call get_stats of all Rule Manager and return all stats.

        :param delete: if true it deletes the stats.
        :type delete: bool
        :return: stats dictionary
        :rtype: dict
        """
        stats = {}
        for rm in self._ruleManagers.values():
            stats.update(rm.get_stats(delete))
        return stats
