import copy
import json
import logging

from routingfilter.configfilter import ConfigFilter


class Routing:

    def __init__(self):
        self.rules = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_rules(self):
        """Return the currently loaded rules. It is mainly used for debugging purposes.

        :return: A dict or None
        """
        return self.rules

    def match(self, event, type_="streams", tag_field_name="tags"):
        """Process a single event message through routing filters and verify if it matches with (at least) one filter.
        For each top level tag in the rule, only the first matching filter is returned.
        Multiple dictionaries can only be returned with rules matching different tags.

        :param event: The entire event to process
        :type event: dict
        :param type_: The event type (can be 'streams', 'customer' or everything else, as defined in the routing config). If the type does not exists, an empty list is returned
        :type type_: str
        :param tag_field_name: The event field to search into (default='tags')
        :type tag_field_name: str
        :return: A list of dicts containing the matched rules and the outputs in the following format: {"rules": [...], "output": {...}}; an empty list if no rule matched
        """
        if not self.rules:
            self.logger.error("'rules_list' must be set before evaluating a match!")
            raise ValueError("'rules_list' must be set before evaluating a match!")
        if type_ not in self.rules:
            return []

        # iterate through the common set of tags
        streams_tags = set(self.rules[type_]["rules"].keys())
        tags = event.get(tag_field_name, [])
        if not isinstance(tags, list):
            tags = [tags]
        tags = set(tags)
        msg_tags = (tags & streams_tags)
        matching_rules = []

        # if in routing stream there is an "all" tag I'm checking it for every msg
        # the "all" routing rules are applied to every msg, to check for those I'm adding the tag in
        # msg_tags so I load and apply the filters on every msg
        # The an "all" rule matches we just return without processing any other rule
        if "all" in streams_tags:
            # the first matching rule wins
            rules = self.rules[type_]["rules"]["all"]
            rules = rules if rules else []
            for rule in rules:
                # check if ALL the filters are matching
                filters = [ConfigFilter(f) for f in rule.get("filters", [])]
                if all(f.is_matching(event) for f in filters):
                    matching_rules.append(rule if rule.get(type_) else {})
        if not matching_rules:
            for tag_field_name in msg_tags:
                for rule in self.rules[type_]["rules"].get(tag_field_name, []):
                    # check if ALL the filters are matching
                    filters = [ConfigFilter(f) for f in rule.get("filters", [])]
                    if filters and all(f.is_matching(event) for f in filters):
                        matching_rules.append(rule)
                        break  # the first matching rule wins
        # Rename "filters" to "rules" and "type" to "output" to be more generic
        matching_rules = copy.deepcopy(matching_rules)
        for mr in matching_rules:
            if "filters" in mr:
                mr["rules"] = mr.pop("filters")
            if type_ in mr:
                mr["output"] = mr.pop(type_)
        return matching_rules

    def load_from_dicts(self, rules_list, validate_rules=True):
        """Load routing configuration from a dictionary. It merges the different rules in list into a single routing rule.
        It optionally performs some rules validation before accepting them (an exception is raised in case of errors).

        :param rules_list: The configuration
        :type rules_list: list[dict]
        :param validate_rules: Perform rules validation (default=True). It can be disabled to improve performance (unsafe)
        :type validate_rules: bool
        """
        self.logger.debug(f"Attempting to load rules_list: {rules_list}")
        rules_list = copy.deepcopy(rules_list)
        if not rules_list:
            self.logger.warning("An empty rules_list has been passed. Makes sure this is intentional.")
            self.rules = {}
            return self.rules
        if not isinstance(rules_list, list):
            self.logger.error("'rules_list' must be a list of dicts containing the routing rules!")
            raise ValueError("'rules_list' must be a list of dicts containing the routing rules!")
        merged_rules = rules_list[0]
        for rules in rules_list[1:]:
            for type_ in rules.keys():
                if type_ in merged_rules:
                    for tag in rules[type_]["rules"].keys():
                        if tag in merged_rules[type_]["rules"]:
                            merged_rules[type_]["rules"][tag] += rules[type_]["rules"][tag]
                        else:
                            merged_rules[type_]["rules"][tag] = rules[type_]["rules"][tag]
                else:
                    merged_rules[type_] = rules[type_]
        self.logger.debug(f"Merged rules: {merged_rules}")
        if validate_rules:
            self._validate_rules(merged_rules)
        self.rules = merged_rules

    def load_from_jsons(self, rules_list, validate_rules=True):
        """Load routing configuration from JSON data. It merges the different rules in list into a single routing rule.
        It optionally performs some rules validation before accepting them (an exception is raised in case of errors).

        :param rules_list: The json data, which will be parsed into a dict
        :type rules_list: list[str]
        :param validate_rules: Perform rules validation (default=True). It can be disabled to improve performance (unsafe)
        :type validate_rules: bool
        """
        if not isinstance(rules_list, str):
            self.logger.error("'rules_list' must be a list of JSON strings containing the routing rules!")
            raise ValueError("'rules_list' must be a list of JSON strings containing the routing rules!")
        self.load_from_dicts(json.loads(rules_list), validate_rules)

    def _validate_rules(self, rules):
        """Validate the loaded rules, checking for type mismatch errors.

        :param rules: The merged rules, after loading them from a list of dicts
        :type rules: dict
        """
        self.logger.info("Validating the loaded rules_list")
        for type_ in rules.keys():
            for tag_ in rules[type_]["rules"].keys():
                for filter_output in rules[type_]["rules"][tag_]:
                    for filter_ in filter_output["filters"]:
                        config_filter_obj = ConfigFilter(filter_)
                        config_filter_obj.is_matching({})
