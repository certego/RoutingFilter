import json
import logging
from typing import List, Optional

from .dictquery import DictQuery
from .filters import filters
from .filters.rule import Rule, RuleManager
from .filters.stream import Stream


class Routing:
    def __init__(self):
        self.streams = Stream("streams")
        self.customer = Stream("customer")
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_stats(self, delete: bool = False) -> dict:
        """
        Call get_stats of streams and return the stats. If delete is True, reset the stats.

        :param delete: If True, delete the stats
        :type delete: bool
        :return: stream and customer stats
        :rtype: dict
        """
        stats = {"streams": self.streams.get_stats(delete), "customer": self.customer.get_stats(delete)}
        return stats

    def match(self, event: dict, type_: str = "streams", tag_field_name: str = "tags") -> List[dict] | List[None]:
        """
        Process a single event message and call the right stream match method.

        :param event: event to check
        :type event: dict
        :param type_: stream type, it can be "streams" or "customer"
        :type type_: str
        :param tag_field_name: the event field to search into
        :type tag_field_name: str
        :return: A list of dictionaries containing the matched rules and the outputs
        :rtype: List[dict]
        """
        event = DictQuery(event)
        # create routing_history if not exists
        if "certego" not in event.keys():
            event["certego"] = {}
        if "routing_history" not in event["certego"]:
            event["certego"]["routing_history"] = {}

        # check stream
        if type_ == "streams":
            stream = self.streams
        elif type_ == "customer":
            stream = self.customer
        else:
            self.logger.error(f"Error during matching. Invalid Stream: {type_}")
            raise ValueError(f"Invalid Stream: {type_}.")

        return stream.match(event, tag_field_name)

    def load_from_dicts(self, rules_list: List[dict], validate_rules: bool = True, variables: Optional[dict] = None) -> None:
        """
        Load routing rule configuration from a dictionary. It instances Filters, Stream, Rule and RuleManager objects by checking dictionaries in rules_list.
        An exception is raised if arguments are invalid.

        :param rules_list: list of dictionary representing routing rule configurations
        :type rules_list: List[dict]
        :param validate_rules:
        :type validate_rules: bool
        :param variables:
        :type variables: Optional[dict]
        :return: no value
        :rtype None
        """
        # check rules_list
        if not isinstance(rules_list, list):
            self.logger.error(f"Invalid argument: {rules_list} is not a list.")
            raise ValueError(f"Invalid argument: {rules_list} is not a list.")
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
                        output = rule["streams"] if rule["streams"] else {}
                        rule_object = Rule(uid="uid", output=output)  # TODO: define uid
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

    def load_from_jsons(self, rule_list: List[str], validate_rules: bool = True, variables: Optional[dict] = None) -> None:
        """
        Load routing rule configurations from json data.

        :param rule_list: list of json string representing routing rule configurations
        :type rule_list: List[str]
        :param validate_rules:
        :type validate_rules: bool
        :param variables:
        :type variables: Optional[dict]
        :return: no value
        :rtype: None
        """
        # TODO: implement variables
        if not isinstance(rule_list, list):
            raise ValueError(f"Invalid rule_list {rule_list}: it must be a list of json data")
        try:
            rule_list[:] = [json.loads(rule) for rule in rule_list]
        except TypeError:
            self.logger.error(f"Invalid rule_list {rule_list}: each rule file must be a string")
            raise ValueError(f"Invalid rule_list {rule_list}: each rule file must be a string")
        except json.decoder.JSONDecodeError:
            self.logger.error(f"Invalid rule_list {rule_list}: each rule file must be a json data")
            raise ValueError(f"Invalid rule_list {rule_list}: each rule file must be a json data")

        self.load_from_dicts(rule_list, validate_rules, variables)
