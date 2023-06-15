import copy
import os
import json
import unittest

from routingfilter.routing import Routing


def load_test_data(name):
    """Load a JSON test file from 'test_data' folder, given its name (extension excluded), and parse it into a dictionary."""
    with open(os.path.join('test_data', name + '.json')) as file:
        data = json.load(file)
    return data


class RoutingTestCase(unittest.TestCase):
    """Class to tests routing.py file. These tests loads sample events from JSON files in 'test_data' folder
    and test if the routing rules are working correctly."""

    def setUp(self):
        self.routing = Routing()
        # Load frequently accessed test data from JSON files
        self.test_event_1 = load_test_data("test_event_1")
        self.test_event_2 = load_test_data("test_event_2")
        self.test_event_3 = load_test_data("test_event_3")
        self.test_event_4 = load_test_data("test_event_4")
        self.test_event_5 = load_test_data("test_event_5")
        self.test_event_6 = load_test_data("test_event_6")
        self.test_event_7 = load_test_data("test_event_7")
        self.test_event_8 = load_test_data("test_event_8")
        self.test_event_9 = load_test_data("test_event_9")
        self.test_event_10 = load_test_data("test_event_10")
        self.test_event_11 = load_test_data("test_event_11")
        self.test_event_12 = load_test_data("test_event_12")
        self.test_event_13 = load_test_data("test_event_13")
        self.test_event_14 = load_test_data("test_event_14")
        self.test_event_15 = load_test_data("test_event_15")
        self.test_event_16 = load_test_data("test_event_16")
        self.test_event_17 = load_test_data("test_event_17")
        self.test_event_18 = load_test_data("test_event_18")
        self.test_event_with_list_1 = load_test_data("test_event_with_list_1")
        self.test_event_with_list_2 = load_test_data("test_event_with_list_2")

    def test_wrong_inputs(self):
        self.assertIsNone(self.routing.get_rules())
        with self.assertRaises(ValueError):
            self.routing.match({})
        self.routing.load_from_dicts([load_test_data("test_rule_1_equals")])
        self.assertEqual(self.routing.match(self.test_event_1, "wrong_type"), [])
        self.assertEqual(self.routing.match({}), [])
        self.routing.load_from_dicts([])
        self.assertDictEqual(self.routing.get_rules(), {})
        with self.assertRaises(ValueError):
            self.routing.load_from_jsons([])

    def test_multiple_rule_loading(self):
        data = load_test_data("test_rule_1_equals")
        rule_list_duplicate = [
            load_test_data("test_rule_11_domain"),
            data,
            load_test_data("test_rule_11_domain"),
            data,
            load_test_data("test_rule_5_exists"),
        ]
        self.routing.load_from_dicts(rule_list_duplicate)
        self.assertEqual(len(self.routing.get_rules()['streams']['rules']['mountain_bike']), 3)
        self.assertEqual(len(self.routing.get_rules()['streams']['rules']['ip_traffic']), 2)
        # Verify that the only first rule matches
        rule_all = load_test_data("test_rule_2_all_equals")
        filter_2 = copy.deepcopy(rule_all["streams"]["rules"]["all"][0])
        filter_2["streams"] = {"Other": None}
        rule_all["streams"]["rules"]["all"].append(filter_2)
        self.routing.load_from_dicts([rule_all])
        self.assertDictEqual(self.routing.match(self.test_event_1)[0]["output"], {'Workshop': {'workers_needed': 1}})

    def test_match_streams_none(self):
        self.routing.load_from_dicts([load_test_data("test_rule_25_routing_history_streams_none")])
        self.routing.match(self.test_event_1)
        self.assertTrue("rules" in self.routing.match(self.test_event_1)[0])
        self.assertTrue("output" in self.routing.match(self.test_event_1)[0])
        self.assertEqual(None, self.routing.match(self.test_event_1)[0]["output"])

    def test_no_match_streams_none(self):
        self.routing.load_from_dicts([load_test_data("test_rule_25_routing_history_streams_none")])
        self.routing.match(self.test_event_4)
        self.assertFalse("rules" in self.routing.match(self.test_event_4))
        self.assertEqual([], self.routing.match(self.test_event_4))
        self.assertFalse("output" in self.routing.match(self.test_event_4))

    def test_routing_history(self):
        self.routing.load_from_dicts([load_test_data("test_rule_24_routing_history")])
        self.routing.match(self.test_event_1)
        self.assertTrue(self.test_event_1["certego"]["routing_history"]["Workshop"])
        # Check if the rule is processed twice
        self.assertTrue("Workshop" in self.test_event_1["certego"]["routing_history"])
        self.assertFalse("TyreFit" in self.test_event_1["certego"]["routing_history"])
        # Just the second rule has to be parsed
        self.routing.match(self.test_event_1)
        self.assertTrue("Workshop" in self.test_event_1["certego"]["routing_history"])
        self.assertTrue("TyreFit" in self.test_event_1["certego"]["routing_history"])
        
    def test_routing_history_stream_none(self):
        self.routing.load_from_dicts([load_test_data("test_rule_1_equals")])
        self.routing.match(self.test_event_1)
        # Match rules
        self.assertTrue(self.test_event_1["certego"]["routing_history"]["Workshop"])
        self.routing.load_from_dicts([load_test_data("test_rule_25_routing_history_streams_none")])
        self.routing.match(self.test_event_1)
        # Checking no match, the message should be filtered
        self.assertEqual(len(self.test_event_1["certego"]["routing_history"].keys()), 1)
        self.assertEqual(None, self.routing.match(self.test_event_1)[0]["output"])

    def test_routing_history_same_rule_twice(self):
        workshop_count = 0
        self.routing.load_from_dicts([load_test_data("test_rule_1_equals")])
        self.routing.match(self.test_event_1)
        self.assertTrue(self.test_event_1["certego"]["routing_history"]["Workshop"])
        self.routing.load_from_dicts([load_test_data("test_rule_1_equals")])
        res = self.routing.match(self.test_event_1)
        for key in self.test_event_1["certego"]["routing_history"].keys():
            if key == "Workshop":
                workshop_count = workshop_count + 1
        self.assertEqual(workshop_count, 1)
        self.assertEqual([], res)

    def test_double_stream(self):
        self.routing.load_from_dicts([load_test_data("test_rule_28_double_stream")])
        res = self.routing.match(self.test_event_1)
        self.assertDictEqual({'Workshop': {'workers_needed': 1}, 'Lab': {'workers_needed': 2}}, res[0]["output"])
        self.assertTrue("Workshop" in self.test_event_1["certego"]["routing_history"])
        self.assertTrue("Lab" in self.test_event_1["certego"]["routing_history"])
        self.assertEqual(2, len(res[0]["output"]))

    def test_double_tag(self):
        self.routing.load_from_dicts([load_test_data("test_rule_29_double_tag")])
        res = self.routing.match(self.test_event_18)
        self.assertEqual(2, len(res))

    def test_rule_1(self):
        # Test rule loading and applying with full output
        self.routing.load_from_dicts([load_test_data("test_rule_1_equals")])
        self.assertDictEqual(self.routing.match(self.test_event_1)[0], load_test_data("test_event_1_rule_1_response"))
        self.assertEqual(self.routing.match(self.test_event_2), [])
        self.assertEqual(self.routing.match(self.test_event_3), [])

    def test_rule_2(self):
        # Same as test_rule_1, but with type "all" (matches all "types")
        self.routing.load_from_dicts([load_test_data("test_rule_2_all_equals")])
        self.assertDictEqual(self.routing.match(self.test_event_1)[0], load_test_data("test_event_1_rule_1_response"))
        self.assertDictEqual(self.routing.match(self.test_event_2)[0], load_test_data("test_event_1_rule_1_response"))
        self.assertEqual(self.routing.match(self.test_event_3), [])

    def test_rule_4(self):
        # Rule 4 contains more than one filter in one rule
        self.routing.load_from_dicts([load_test_data("test_rule_4_multiple_filters")])
        self.assertDictEqual(self.routing.match(self.test_event_1)[0], load_test_data("test_event_1_rule_4_response"))
        self.assertEqual(self.routing.match(self.test_event_2), [])
        self.assertEqual(self.routing.match(self.test_event_3), [])

    def test_merged_rules(self):
        # Merge two rules with same "type". Fully tests the method "load_from_dicts"
        test_rule_1_equals = load_test_data("test_rule_1_equals")
        self.routing.load_from_dicts([test_rule_1_equals, load_test_data("test_rule_2_all_equals")])
        self.assertDictEqual(self.routing.get_rules(), load_test_data("merge_rules_1_2"))
        self.routing.load_from_dicts([test_rule_1_equals, load_test_data("test_rule_3_customer_equals")])
        self.assertDictEqual(self.routing.get_rules(), load_test_data("merge_rules_1_3"))
        self.routing.load_from_dicts([test_rule_1_equals, load_test_data("test_rule_4_multiple_filters")])
        self.assertDictEqual(self.routing.get_rules(), load_test_data("merge_rules_1_4"))

    def test_special_tag_all(self):
        # Test merge with special tag 'all' (matches all tags)
        test_rule_1_equals = load_test_data("test_rule_1_equals")
        test_rule_2_all_equals = load_test_data("test_rule_2_all_equals")
        self.routing.load_from_dicts([test_rule_1_equals, test_rule_2_all_equals])
        self.assertDictEqual(self.routing.match(self.test_event_1)[0], load_test_data("test_event_1_rule_1_response"))
        self.assertDictEqual(self.routing.match(self.test_event_2)[0], load_test_data("test_event_1_rule_1_response"))
        self.assertEqual(self.routing.match(self.test_event_3), [])
        
    def test_special_tag_all2(self):
        test_rule_1_equals = load_test_data("test_rule_1_equals")
        test_rule_2_all_equals = load_test_data("test_rule_2_all_equals")
        test_rule_2_all_equals["streams"]["rules"]["all"][0]["filters"][0]["key"] = "wheel_model_wrong"
        self.routing.load_from_dicts([test_rule_1_equals, test_rule_2_all_equals])
        self.assertDictEqual(self.routing.match(self.test_event_1)[0], load_test_data("test_event_1_rule_1_response"))
        self.assertEqual(self.routing.match(load_test_data("test_event_2")), [])

    def test_event_with_multiple_tags(self):
        test_rule_1_equals = load_test_data("test_rule_1_equals")
        test_rule_9_network = load_test_data("test_rule_9_network")
        test_rule_9_network["streams"]["rules"]["ip_traffic"][0]["streams"] = {"metatada": 123}
        self.routing.load_from_dicts([test_rule_1_equals])
        self.assertDictEqual(self.routing.match(self.test_event_6)[0], load_test_data("test_event_1_rule_1_response"))
        self.assertFalse(self.routing.match(self.test_event_2))
        self.routing.load_from_dicts([test_rule_1_equals, test_rule_9_network])
        test_event_4_mod = copy.deepcopy(self.test_event_4)
        test_event_4_mod["tags"] = ["ip_traffic", "mountain_bike"]
        test_event_4_mod["wheel_model"] = "Superlight"
        self.assertEqual(len(self.routing.match(test_event_4_mod)), 2)

    def test_event_wrong_field_name(self):
        test_rule_7 = load_test_data("test_rule_7_wrongfield")
        self.routing.load_from_dicts([test_rule_7])
        self.assertEqual(self.routing.match(self.test_event_7), [])

    def test_single_filters_ALL(self):
        self.routing.load_from_dicts([load_test_data("test_rule_0_all")])  # ALL
        self.assertTrue(self.routing.match(self.test_event_1))
        self.assertFalse(self.routing.match(self.test_event_2))
        self.assertTrue(self.routing.match(self.test_event_3))
        self.assertFalse(self.routing.match(self.test_event_4))

    def test_single_filters_EQUALS(self):
        self.routing.load_from_dicts([load_test_data("test_rule_1_equals")])  # EQUALS
        self.assertTrue(self.routing.match(self.test_event_1))
        self.assertFalse(self.routing.match(self.test_event_3))
    
    def test_single_filters_NOT_EQUALS(self):
        self.routing.load_from_dicts([load_test_data("test_rule_1_not_equals")])  # NOT EQUALS
        self.assertFalse(self.routing.match(self.test_event_1))
        self.assertTrue(self.routing.match(self.test_event_3))

    def test_single_filters_STARTSWITH(self):
        self.routing.load_from_dicts([load_test_data("test_rule_6_startswith")])  # STARTSWITH
        self.assertTrue(self.routing.match(self.test_event_1))
        self.assertFalse(self.routing.match(self.test_event_3))

    def test_single_filters_KEYWORD(self):
        self.routing.load_from_dicts([load_test_data("test_rule_7_keyword")])  # KEYWORD
        self.assertTrue(self.routing.match(self.test_event_1))
        self.assertFalse(self.routing.match(self.test_event_3))

    def test_single_filters_REGEXP(self):
        self.routing.load_from_dicts([load_test_data("test_rule_8_regexp")])  # REGEXP
        self.assertTrue(self.routing.match(self.test_event_1))
        self.assertFalse(self.routing.match(self.test_event_3))

    def test_single_filters_DOMAIN(self):
        self.routing.load_from_dicts([load_test_data("test_rule_11_domain")])  # DOMAIN
        self.assertTrue(self.routing.match(self.test_event_4))
        self.assertFalse(self.routing.match(self.test_event_5))

    def test_single_filters_GREATER(self):
        self.routing.load_from_dicts([load_test_data("test_rule_12_greater")])  # GREATER
        self.assertFalse(self.routing.match({}))
        self.assertTrue(self.routing.match(self.test_event_1))
        self.assertFalse(self.routing.match(self.test_event_3))
        with self.assertRaises(ValueError):
            event_2 = self.test_event_2
            event_2["tags"] = "mountain_bike"
            event_2["price"] = "600a"
            self.routing.match(event_2)
        
    def test_single_filters_LESS(self):
        self.routing.load_from_dicts([load_test_data("test_rule_13_less")])  # LESS
        self.assertFalse(self.routing.match(self.test_event_1))
        self.assertTrue(self.routing.match(self.test_event_3))

    def test_single_filters_ENDSSWITH(self):
        self.routing.load_from_dicts([load_test_data("test_rule_14_endswith")])  # ENDSSWITH
        self.assertTrue(self.routing.match(self.test_event_1))
        self.assertFalse(self.routing.match(self.test_event_3))
        self.assertFalse(self.routing.match(self.test_event_8))

    def test_single_filter_EXIST(self):
        self.routing.load_from_dicts([load_test_data("test_rule_5_exists")])  # EXISTS
        self.assertTrue(self.routing.match(self.test_event_1))
        self.assertFalse(self.routing.match(self.test_event_3))
        self.assertTrue(self.routing.match(self.test_event_10))
    
    def test_single_filter_NOT_EXISTS(self):
        self.routing.load_from_dicts([load_test_data("test_rule_6_not_exists")])  # NOT_EXISTS
        self.assertFalse(self.routing.match(self.test_event_1))
        self.assertTrue(self.routing.match(self.test_event_3))
        self.assertFalse(self.routing.match(self.test_event_10))

    def test_single_filter_NETWORK(self):
        self.routing.load_from_dicts([load_test_data("test_rule_9_network")])  # NETWORK
        self.assertTrue(self.routing.match(self.test_event_4))
        self.assertFalse(self.routing.match(self.test_event_9))
        self.assertFalse(self.routing.match(self.test_event_6))  # Unparsable

    def test_single_filter_NOT_NETWORK(self):
        self.routing.load_from_dicts([load_test_data("test_rule_10_not_network")])  # NOT_NETWORK
        self.assertFalse(self.routing.match(self.test_event_4))
        self.assertTrue(self.routing.match(self.test_event_5))
        self.assertFalse(self.routing.match(self.test_event_3))
        self.assertTrue(self.routing.match(self.test_event_9))
        self.assertTrue(self.routing.match(self.test_event_6))  # Unparsable

    def test_event_with_lists_as_fields(self):
        self.routing.load_from_dicts([load_test_data("test_rule_9_network")])  # NETWORK
        self.assertTrue(self.routing.match(self.test_event_with_list_1))

        self.routing.load_from_dicts([load_test_data("test_rule_1_equals")])
        self.assertTrue(self.routing.match(self.test_event_with_list_2))

    def test_single_filter_TYPEOF_exception(self):
        # if self.value is a list, it returns True if almost one type is correct
        self.routing.load_from_dicts([load_test_data("test_rule_15_typeof_exception")]) # "value": ["str", "int", "dict"]
        self.assertTrue(self.routing.match(self.test_event_8))      # value: "str"
        self.assertTrue(self.routing.match(self.test_event_11))     # value: "int"
        self.assertTrue(self.routing.match(self.test_event_13))     # value: "dict"
        self.assertFalse(self.routing.match(self.test_event_12))

    def test_single_filter_TYPEOF_str(self):
        self.routing.load_from_dicts([load_test_data("test_rule_16_typeof_str")])   # is_str
        self.assertTrue(self.routing.match(self.test_event_8))
        self.assertFalse(self.routing.match(self.test_event_10))    # is_not_str

    def test_single_filter_TYPEOF_int(self):
        self.routing.load_from_dicts([load_test_data("test_rule_17_typeof_int")])   # is_int
        self.assertTrue(self.routing.match(self.test_event_11))
        self.assertFalse(self.routing.match(self.test_event_8))     # is_not_int

    def test_single_filter_TYPEOF_bool(self):
        self.routing.load_from_dicts([load_test_data("test_rule_18_typeof_bool")])   # is_bool
        self.assertTrue(self.routing.match(self.test_event_12))
        self.assertFalse(self.routing.match(self.test_event_8))     # is_not_bool
    
    def test_single_filter_TYPEOF_list(self):
        self.routing.load_from_dicts([load_test_data("test_rule_19_typeof_list")])  # is_list
        self.assertTrue(self.routing.match(self.test_event_10))
        self.assertFalse(self.routing.match(self.test_event_8))    # is_not_list

    def test_single_filter_TYPEOF_dict(self):
        self.routing.load_from_dicts([load_test_data("test_rule_20_typeof_dict")])  # is_dict
        self.assertTrue(self.routing.match(self.test_event_13))
        self.assertFalse(self.routing.match(self.test_event_11))    # is_not_dict

    def test_single_filter_TYPEOF_ip_address(self):
        self.routing.load_from_dicts([load_test_data("test_rule_21_typeof_ip")])  # is_ipv4
        self.assertTrue(self.routing.match(self.test_event_15))
        self.assertTrue(self.routing.match(self.test_event_16))     # is_ipv6
        self.assertFalse(self.routing.match(self.test_event_11))    # insert an integer
        self.assertFalse(self.routing.match(self.test_event_14))    # insert a string with a number: ex. "8"
        self.assertFalse(self.routing.match(self.test_event_12))    # is_not_ip

    def test_single_filter_TYPEOF_mac_address(self):
        self.routing.load_from_dicts([load_test_data("test_rule_22_typeof_mac")])    # is_mac
        self.assertTrue(self.routing.match(self.test_event_17))
        self.assertFalse(self.routing.match(self.test_event_16))    # is_not_mac
        # key doesn't exist
        self.assertFalse(self.routing.match(self.test_event_5))

    def test_variables_no_list(self):
        self.routing.load_from_dicts([load_test_data("test_rule_23_network_variables")])
        self.assertFalse(self.routing.match(self.test_event_4))
        self.routing.load_from_dicts([load_test_data("test_rule_23_network_variables")], variables={"$INTERNAL_IPS": "192.168.1.0/24"})
        self.assertTrue(self.routing.match(self.test_event_4))
    
    def test_variables_list_one_element(self): 
        self.routing.load_from_dicts([load_test_data("test_rule_26_network_variables_list1")], variables={"$INTERNAL_IPS": "192.168.1.0/24"})
        self.assertTrue(self.routing.match(self.test_event_4))
    
    def test_variables_list_more_elements(self):
        self.routing.load_from_dicts([load_test_data("test_rule_27_network_variables_list2")], variables={"$INTERNAL_IPS": ["192.168.1.0/24", "192.168.2.0/24"]})
        self.assertTrue(self.routing.match(self.test_event_4))

    def test_rule_in_routing_history(self):
        event = {"certego": {"routing_history": {}}}
        rule = {
            "filters": [
              {
                "type": "EQUALS",
                "key": "wheel_model",
                "description": "Carbon fiber wheels needs manual truing",
                "value": [
                  "Superlight",
                  "RacePro"
                ]
              }
            ],
            "streams": {
            }
          }
        self.assertFalse(self.routing.rule_in_routing_history(event, rule))
        event = {"certego": {"routing_history": {"Workshop": "2023-06-06T18:00:00.000Z"}}}
        self.assertFalse(self.routing.rule_in_routing_history(event, rule))
        rule = {
            "filters": [
              {
                "type": "EQUALS",
                "key": "wheel_model",
                "description": "Carbon fiber wheels needs manual truing",
                "value": [
                  "Superlight",
                  "RacePro"
                ]
              }
            ],
            "streams": {
                "Workshop": {
                    "workers_needed": 1
                }
            }
          }
        self.assertTrue(self.routing.rule_in_routing_history(event, rule))


