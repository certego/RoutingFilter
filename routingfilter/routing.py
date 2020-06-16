import copy
import json

from routingfilter.configfilter import ConfigFilter


class Routing:

    def __init__(self):
        self.rules = None

    def match(self, event, type_="streams", tag_field_name="tags"):
        """Process a single event message through routing filters and verify if it matches with (at least) one filter.

        :param event: The entire event to process
        :type event: dict
        :param type_: The event type (can be 'streams', 'customer' or everything else, as defined in the routing config)
        :type type_: str
        :param tag_field_name: The event field to search into (default='tags')
        :type tag_field_name: str
        :return: A dict containing a list of the matched rules and the outputs in the following format: {"rules": [...], "output": {...}}
        """
        if not self.rules:
            raise ValueError("'rules_list' must be set before evaluating a match!")

        # iterate through the common set of tags
        streams_tags = set(self.rules[type_]["rules"].keys())
        tags = event.get(tag_field_name, [])
        if not isinstance(tags, list):
            tags = [tags]
        tags = set(tags)
        msg_tags = (tags & streams_tags)
        matching_rules = {}

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
                    matching_rules.update(rule if rule.get(type_) else {})
        else:
            for tag_field_name in msg_tags:
                for rule in self.rules[type_]["rules"].get(tag_field_name, []):
                    # check if ALL the filters are matching
                    filters = [ConfigFilter(f) for f in rule.get("filters", [])]
                    if all(f.is_matching(event) for f in filters):
                        matching_rules.update(rule)
                        # output = rule.get(type, {})
                        # if output:
                        #     matching_rules.update(output)
                        break  # the first matching rule wins
        # Rename "filters" to "rules" and "type" to "output" to be more generic
        if "filters" in matching_rules:
            matching_rules["rules"] = matching_rules.pop("filters")
        if type_ in matching_rules:
            matching_rules["output"] = matching_rules.pop(type_)
        return matching_rules

    def load_from_dicts(self, rules_list):
        """Load routing configuration from a dictionary. It merges the different rules in list into a single routing rule.

        :param rules_list: The configuration
        :type rules_list: list[dict]
        :return: The merged rule set which has been applied
        """
        rules_list = copy.deepcopy(rules_list)
        if not rules_list:
            self.rules = {}
            return self.rules
        if not isinstance(rules_list, list):
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
        self.rules = merged_rules
        return merged_rules

    def load_from_jsons(self, rules_list):
        """Load routing configuration from JSON data. It merges the different rules in list into a single routing rule.

        :param rules_list: The json data, which will be parsed into a dict
        :type rules_list: list[str]
        """
        if not isinstance(rules_list, str):
            raise ValueError("'rules_list' must be a list of JSON strings containing the routing rules!")
        self.load_from_dicts(json.loads(rules_list))
