import logging
from typing import List, Optional

from routingfilter.dictquery import DictQuery
from rule import RuleManager


class Stream:
    def __init__(self, stream):
        self.stream = stream
        self._ruleManagers = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def match(self, event: DictQuery) -> List[dict] | List[None]:
        """
        Call all ruleManagers that contain tha tag of event "tags" field (that could be a list).
        It returns a list of dictionaries representing eventual matches or None if no matches are found.
        If a RuleManager has the tag "all", match method must be called before any. If there is a match, it returns
        immediately the result without check RuleManager for other tag.

        :param event: event to check
        :type event: DictQuery
        :return: list of matches or None otherwise
        :rtype: List[dict] | List[None]
        """
        match_list = []
        tags = event.get("tags")
        if not isinstance(tags, list):
            tags = [tags]
        # tag all
        if "all" in self._ruleManagers.keys():
            all_match = self._ruleManagers["all"].match(event)
            if all_match is not None:
                return [all_match]
        for tag in tags:
            # append dict or None
            if tag in self._ruleManagers.keys():
                match_list.append(self._ruleManagers[tag].match(event))
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
            stats.update({self.stream: rm.get_stats(delete)})  # TODO: it's okay the key?
        return stats
