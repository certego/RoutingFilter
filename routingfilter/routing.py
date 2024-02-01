import logging
from typing import List, Optional

from filters import filters
from filters.rule import Rule, RuleManager
from filters.stream import Stream


class Routing:
    def __init__(self):
        self.streams = Stream("streams")
        self.customer = Stream("customer")
        self.logger = logging.getLogger(self.__class__.__name__)

    def load_from_dicts(self, rules_list: List[dict], validate_rules: bool = True, variables: Optional[dict] = None) -> None:
        """

        :param rules_list:
        :param validate_rules:
        :param variables:
        :return:
        """
        for rule_file in rules_list:
            # access to stream
            for stream_type in rule_file.keys():
                # check stream
                if stream_type == "streams":
                    streams = self.streams
                elif stream_type == "customer":
                    streams = self.customer
                else:
                    self.logger.error(f"Error during loading rule. Invalid Stream: {stream_type}")
                    raise ValueError(f"Invalid Stream: {stream_type}.")

                for tag in rule_file[stream_type]["rules"].keys():
                    # check if rule manager with tag exists
                    if tag in streams._ruleManagers.keys():
                        rule_manager = streams._ruleManagers[tag]
                    else:
                        rule_manager = RuleManager(tag)
                        streams.add_rulemanager(rule_manager)
                    for rule in rule_file[stream_type]["rules"][tag]:
                        # add rule to rule manager and filters to rule
                        rule_object = Rule(uid="uid", output=rule["streams"])  # TODO: define uid
                        rule_manager.add_rule(rule_object)
                        filter_list = self._get_filters(rule)
                        rule_object.add_filter(filter_list)

    def _get_filters(self, rule: dict) -> List[filters.AbstractFilter]:
        """
        Get filters by checking rule dictionary.

        :param rule: rule dictionary containing filters
        :type rule: dict
        :return: list of filters
        :rtype: List[filters.AbstractFilter]
        """
        filters_list = []
        for el in rule["filters"]:
            keys = el["key"] if "key" in el.keys() else None
            values = el["value"] if "value" in el.keys() else None
            new_filter = None
            match el["type"]:
                case "ALL":
                    new_filter = filters.AllFilter()
                case "EXISTS":
                    new_filter = filters.ExistFilter(keys)
                case "NOT_EXISTS":
                    new_filter = filters.NotExistFilter(keys)
                case "EQUALS":
                    new_filter = filters.EqualFilter(keys, values)
                case "STARTSWITH":
                    new_filter = filters.StartswithFilter(keys, values)
                case "ENDSWITH":
                    new_filter = filters.EndswithFilter(keys, values)
                case "KEYWORD":
                    new_filter = filters.Keywordfilter(keys, values)
                case "REGEXP":
                    new_filter = filters.RegexpFilter(keys, values)
                case "NETWORK":
                    new_filter = filters.NetworkFilter(keys, values)
                case "NOT_NETWORK":
                    new_filter = filters.NotNetworkFilter(keys, values)
                case "DOMAIN":
                    new_filter = filters.DomainFilter(keys, values)
                case "GREATER" | "LESS" | "LESS_EQ" | "GREATER_EQ":
                    new_filter = filters.ComparatorFilter(keys, values, el["type"])
                case "TYPEOF":
                    new_filter = filters.TypeofFilter(keys, values)

            filters_list.append(new_filter)
        return filters_list
