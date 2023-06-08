from datetime import datetime
import json
import os
from typing import List

from routingfilter.routing import Routing

def load_test_data(name):
    """Load a JSON test file from 'test_data' folder, given its name (extension excluded), and parse it into a dictionary."""
    with open(os.path.join('test_data', name + '.json')) as file:
        data = json.load(file)
    return data

MAX_RULE = 1000
MAX_EVENT = 100
MAX_LIST_VALUES = 100

class RoutingBenchMark():
    """Class to test the routing performance in order to monitor the trend of the execution time after new features or changes"""       
    
    def test1_EQUALS_no_key_match(self):
        """Performance test, for the EQUALS routing filter type, with:
            - 100 same rules (type: EQUALS)
            - 100 messages with 50 fields different from 'wheel_model'
        """
        self.routing = Routing()
        my_dict = load_test_data("benchmark_rule_equals_dict")
        # Create 100 EQUALS same rules
        rule = load_test_data("benchmark_rule_equals")
        for i in range(MAX_RULE):
            rule["streams"]["rules"]["mountain_bike"].append(my_dict)
        self.benchmark_event_1 = load_test_data("benchmark_event_1")
        self.routing.load_from_dicts([rule])
        start_time = datetime.now()
        # Sending 100 messages to the routing
        for i in range(MAX_EVENT):
            self.routing.match(self.benchmark_event_1)
        end_time = datetime.now()
        print(f"{self.test1_EQUALS_no_key_match.__name__}: {(end_time - start_time).total_seconds()}")

    def test2_EQUALS_key_exists(self):
        """Performance test, for the EQUALS routing filter type, with:
            - 100 same rules (type: EQUALS)
            - 100 messages with 50 fields (one of them 'wheel_model' but not 'Superlight'
        """
        self.routing = Routing()
        my_dict = load_test_data("benchmark_rule_equals_dict")
        # Create 100 EQUALS same rules
        rule = load_test_data("benchmark_rule_equals")
        for i in range(MAX_RULE):
            rule["streams"]["rules"]["mountain_bike"].append(my_dict)
        self.benchmark_event_1 = load_test_data("benchmark_event_1")
        # Adding the field 'wheel_model' but with a value different from 'Superlight'
        self.benchmark_event_1.update({"wheel_model": "test"})
        self.routing.load_from_dicts([rule])
        start_time = datetime.now()
        # Sending 100 messages to the routing
        for i in range(MAX_EVENT):
            self.routing.match(self.benchmark_event_1)
        end_time = datetime.now()
        print(f"{self.test2_EQUALS_key_exists.__name__}: {(end_time - start_time).total_seconds()}")
    
    def test3_EQUALS_list_values(self):
        """Performance test, for the EQUALS routing filter type, with:
            - 100 same rules (type: EQUALS)
            - 100 messages with 50 fields (one of them 'wheel_model' but not 'Superlight'
            - 100 different values in the rules (no matches with the message field)
        """
        self.routing = Routing()
        my_dict = load_test_data("benchmark_rule_equals_dict")
        # Create a list of 100 values in the "value" field of the rule
        for i in range(MAX_LIST_VALUES):
            my_dict["filters"][0]["value"].append("test-" + str(i))
        rule = load_test_data("benchmark_rule_equals")
        # Create 100 EQUALS same rules with 100 values
        for i in range(MAX_RULE):
            rule["streams"]["rules"]["mountain_bike"].append(my_dict)
        self.benchmark_event_1 = load_test_data("benchmark_event_1")
        self.benchmark_event_1.update({"wheel_model": "test"})
        self.routing.load_from_dicts([rule])
        start_time = datetime.now()
        # Sending 100 messages to the routing
        for i in range(MAX_EVENT):
            self.routing.match(self.benchmark_event_1)
        end_time = datetime.now()
        print(f"{self.test3_EQUALS_list_values.__name__}: {(end_time - start_time).total_seconds()}")

    def test4_EQUALS_list_values_message(self):
        """Performance test, for the EQUALS routing filter type, with:
            - 100 values in the "wheel_model" of the rule and of the message, but none of them triggers a match (no 'Superlight')
        """
        self.routing = Routing()
        my_dict = load_test_data("benchmark_rule_equals_dict")
        # Create a list of 100 values in the "value" field of the rule
        for i in range(MAX_LIST_VALUES):
            my_dict["filters"][0]["value"].append("test-" + str(i))
        rule = load_test_data("benchmark_rule_equals")
        # Create 100 EQUALS same rules with 100 values
        for i in range(MAX_RULE):
            rule["streams"]["rules"]["mountain_bike"].append(my_dict)
        self.routing.load_from_dicts([rule])
        # Create a list of values in the message for "wheel_model"
        self.benchmark_event_1 = load_test_data("benchmark_event_1")
        self.benchmark_event_1.update({"wheel_model": []})
        for i in range(MAX_LIST_VALUES):
            self.benchmark_event_1["wheel_model"].append("test-" + str(i))
        start_time = datetime.now()
        # Sending 100 messages to the routing
        for i in range(MAX_EVENT):
            self.routing.match(self.benchmark_event_1)
        end_time = datetime.now()
        print(f"{self.test4_EQUALS_list_values_message.__name__}: {(end_time - start_time).total_seconds()}")

    def test1_STARTSWITH_no_key_match(self):
        """Performance test, for the STARTSWITH routing filter type, with:
            - 100 same rules (type: STARTSWITH)
            - 100 messages with 50 fields different from 'wheel_model'
        """
        self.routing = Routing()
        my_dict = load_test_data("benchmark_rule_startswith_dict")
        # Create 100 EQUALS same rules 
        rule = load_test_data("benchmark_rule_startswith")
        for i in range(MAX_RULE):
            rule["streams"]["rules"]["mountain_bike"].append(my_dict)
        self.benchmark_event_1 = load_test_data("benchmark_event_1")
        self.routing.load_from_dicts([rule])
        start_time = datetime.now()
        # Sending 100 messages to the routing
        for i in range(MAX_EVENT):
            self.routing.match(self.benchmark_event_1)
        end_time = datetime.now()
        print(f"{self.test1_STARTSWITH_no_key_match.__name__}: {(end_time - start_time).total_seconds()}")

    def test2_STARTSWITH_key_exists(self):
        """Performance test, for the STARTSWITH routing filter type, with:
            - 100 same rules (type: STARTSWITH)
            - 100 messages with 50 fields (one of them 'wheel_model' but not 'Superlight'
        """
        self.routing = Routing()
        my_dict = load_test_data("benchmark_rule_startswith_dict")
        # Create 100 EQUALS same rules
        rule = load_test_data("benchmark_rule_startswith")
        for i in range(MAX_RULE):
            rule["streams"]["rules"]["mountain_bike"].append(my_dict)
        self.benchmark_event_1 = load_test_data("benchmark_event_1")
        # Adding the field 'wheel_model' but with a value different from 'Superlight'
        self.benchmark_event_1.update({"wheel_model": "test"})
        self.routing.load_from_dicts([rule])
        start_time = datetime.now()
        # Sending 100 messages to the routing
        for i in range(MAX_EVENT):
            self.routing.match(self.benchmark_event_1)
        end_time = datetime.now()
        print(f"{self.test2_STARTSWITH_key_exists.__name__}: {(end_time - start_time).total_seconds()}")

    def test3_STARTSWITH_list_values(self):
        """Performance test, for the STARTSWITH routing filter type, with:
            - 100 same rules (type: STARTSWITH)
            - 100 messages with 50 fields (one of them 'wheel_model' but not 'Superlight'
            - 100 different values in the rules (no matches with the message field)
        """
        self.routing = Routing()
        my_dict = load_test_data("benchmark_rule_startswith_dict")
        # Create a list of 100 values in the "value" field of the rule
        for i in range(MAX_LIST_VALUES):
            my_dict["filters"][0]["value"].append("test-" + str(i))
        rule = load_test_data("benchmark_rule_startswith")
        # Create 100 EQUALS same rules with 100 values
        for i in range(MAX_RULE):
            rule["streams"]["rules"]["mountain_bike"].append(my_dict)
        self.benchmark_event_1 = load_test_data("benchmark_event_1")
        self.benchmark_event_1.update({"wheel_model": "test"})
        self.routing.load_from_dicts([rule])
        start_time = datetime.now()
        # Sending 100 messages to the routing
        for i in range(MAX_EVENT):
            self.routing.match(self.benchmark_event_1)
        end_time = datetime.now()
        print(f"{self.test3_STARTSWITH_list_values.__name__}: {(end_time - start_time).total_seconds()}")

    def test4_STARTSWITH_list_values_exists(self):
        """Performance test, for the EQUALS routing filter type, with:
            - 100 values in the "wheel_model" of the rule and of the message, but none of them triggers a match (no 'Superlight')
        """
        self.routing = Routing()
        my_dict = load_test_data("benchmark_rule_startswith_dict")
        # Create a list of 100 values in the "value" field of the rule
        for i in range(MAX_LIST_VALUES):
            my_dict["filters"][0]["value"].append("test-" + str(i))
        rule = load_test_data("benchmark_rule_startswith")
        # Create 100 EQUALS same rules with 100 values
        for i in range(MAX_RULE):
            rule["streams"]["rules"]["mountain_bike"].append(my_dict)
        self.routing.load_from_dicts([rule])
        # Create a list of values in the message for "wheel_model"
        self.benchmark_event_1 = load_test_data("benchmark_event_1")
        self.benchmark_event_1.update({"wheel_model": []})
        for i in range(MAX_LIST_VALUES):
            self.benchmark_event_1["wheel_model"].append("test-" + str(i))
        start_time = datetime.now()
        # Sending 100 messages to the routing
        for i in range(MAX_EVENT):
            self.routing.match(self.benchmark_event_1)
        end_time = datetime.now()
        print(f"{self.test4_STARTSWITH_list_values_exists.__name__}: {(end_time - start_time).total_seconds()}")

    def test1_ENDSWITH_no_key_match(self):
        """Performance test, for the ENDSWITH routing filter type, with:
            - 100 same rules (type: ENDSWITH)
            - 100 messages with 50 fields different from 'wheel_model'
        """
        self.routing = Routing()
        my_dict = load_test_data("benchmark_rule_endswith_dict")
        # Create 100 EQUALS same rules 
        rule = load_test_data("benchmark_rule_endswith")
        for i in range(MAX_RULE):
            rule["streams"]["rules"]["mountain_bike"].append(my_dict)
        self.benchmark_event_1 = load_test_data("benchmark_event_1")
        self.routing.load_from_dicts([rule])
        start_time = datetime.now()
        # Sending 100 messages to the routing
        for i in range(MAX_EVENT):
            self.routing.match(self.benchmark_event_1)
        end_time = datetime.now()
        print(f"{self.test1_ENDSWITH_no_key_match.__name__}: {(end_time - start_time).total_seconds()}")

    def test2_ENDSWITH_key_exists(self):
        """Performance test, for the ENDSWITH routing filter type, with:
            - 100 same rules (type: ENDSWITH)
            - 100 messages with 50 fields (one of them 'wheel_model' but not 'Superlight'
        """
        self.routing = Routing()
        my_dict = load_test_data("benchmark_rule_endswith_dict")
        # Create 100 EQUALS same rules
        rule = load_test_data("benchmark_rule_endswith")
        for i in range(MAX_RULE):
            rule["streams"]["rules"]["mountain_bike"].append(my_dict)
        self.benchmark_event_1 = load_test_data("benchmark_event_1")
        # Adding the field 'wheel_model' but with a value different from 'Superlight'
        self.benchmark_event_1.update({"wheel_model": "test"})
        self.routing.load_from_dicts([rule])
        start_time = datetime.now()
        # Sending 100 messages to the routing
        for i in range(MAX_EVENT):
            self.routing.match(self.benchmark_event_1)
        end_time = datetime.now()
        print(f"{self.test2_ENDSWITH_key_exists.__name__}: {(end_time - start_time).total_seconds()}")

    def test3_ENDSWITH_list_values(self):
        """Performance test, for the ENDSWITH routing filter type, with:
            - 100 same rules (type: ENDSWITH)
            - 100 messages with 50 fields (one of them 'wheel_model' but not 'Superlight'
            - 100 different values in the rules (no matches with the message field)
        """
        self.routing = Routing()
        my_dict = load_test_data("benchmark_rule_endswith_dict")
        # Create a list of 100 values in the "value" field of the rule
        for i in range(MAX_LIST_VALUES):
            my_dict["filters"][0]["value"].append("test-" + str(i))
        rule = load_test_data("benchmark_rule_endswith")
        # Create 100 EQUALS same rules with 100 values
        for i in range(MAX_RULE):
            rule["streams"]["rules"]["mountain_bike"].append(my_dict)
        self.benchmark_event_1 = load_test_data("benchmark_event_1")
        self.benchmark_event_1.update({"wheel_model": "test"})
        self.routing.load_from_dicts([rule])
        start_time = datetime.now()
        # Sending 100 messages to the routing
        for i in range(MAX_EVENT):
            self.routing.match(self.benchmark_event_1)
        end_time = datetime.now()
        print(f"{self.test3_ENDSWITH_list_values.__name__}: {(end_time - start_time).total_seconds()}")

    def test4_ENDSWITH_list_values_exists(self):
        """Performance test, for the ENDSWITH routing filter type, with:
            - 100 values in the "wheel_model" of the rule and of the message, but none of them triggers a match (no 'Superlight')
        """
        self.routing = Routing()
        my_dict = load_test_data("benchmark_rule_endswith_dict")
        # Create a list of 100 values in the "value" field of the rule
        for i in range(MAX_LIST_VALUES):
            my_dict["filters"][0]["value"].append("test-" + str(i))
        rule = load_test_data("benchmark_rule_endswith")
        # Create 100 EQUALS same rules with 100 values
        for i in range(MAX_RULE):
            rule["streams"]["rules"]["mountain_bike"].append(my_dict)
        self.routing.load_from_dicts([rule])
        # Create a list of values in the message for "wheel_model"
        self.benchmark_event_1 = load_test_data("benchmark_event_1")
        self.benchmark_event_1.update({"wheel_model": []})
        for i in range(MAX_LIST_VALUES):
            self.benchmark_event_1["wheel_model"].append("test-" + str(i))
        start_time = datetime.now()
        # Sending 100 messages to the routing
        for i in range(MAX_EVENT):
            self.routing.match(self.benchmark_event_1)
        end_time = datetime.now()
        print(f"{self.test4_ENDSWITH_list_values_exists.__name__}: {(end_time - start_time).total_seconds()}")

    def test1_KEYWORD_no_key_match(self):
        """Performance test, for the KEYWORD routing filter type, with:
            - 100 same rules (type: KEYWORD)
            - 100 messages with 50 fields different from 'wheel_model'
        """
        self.routing = Routing()
        my_dict = load_test_data("benchmark_rule_keyword_dict")
        # Create 100 EQUALS same rules 
        rule = load_test_data("benchmark_rule_keyword")
        for i in range(MAX_RULE):
            rule["streams"]["rules"]["mountain_bike"].append(my_dict)
        self.benchmark_event_1 = load_test_data("benchmark_event_1")
        self.routing.load_from_dicts([rule])
        start_time = datetime.now()
        # Sending 100 messages to the routing
        for i in range(MAX_EVENT):
            self.routing.match(self.benchmark_event_1)
        end_time = datetime.now()
        print(f"{self.test1_KEYWORD_no_key_match.__name__}: {(end_time - start_time).total_seconds()}")

    def test2_KEYWORD_key_exists(self):
        """Performance test, for the KEYWORD routing filter type, with:
            - 100 same rules (type: KEYWORD)
            - 100 messages with 50 fields (one of them 'wheel_model' but not 'Superlight'
        """
        self.routing = Routing()
        my_dict = load_test_data("benchmark_rule_keyword_dict")
        # Create 100 EQUALS same rules
        rule = load_test_data("benchmark_rule_keyword")
        for i in range(MAX_RULE):
            rule["streams"]["rules"]["mountain_bike"].append(my_dict)
        self.benchmark_event_1 = load_test_data("benchmark_event_1")
        # Adding the field 'wheel_model' but with a value different from 'Superlight'
        self.benchmark_event_1.update({"wheel_model": "test"})
        self.routing.load_from_dicts([rule])
        start_time = datetime.now()
        # Sending 100 messages to the routing
        for i in range(MAX_EVENT):
            self.routing.match(self.benchmark_event_1)
        end_time = datetime.now()
        print(f"{self.test2_KEYWORD_key_exists.__name__}: {(end_time - start_time).total_seconds()}")

    def test3_KEYWORD_list_values(self):
        """Performance test, for the KEYWORD routing filter type, with:
            - 100 same rules (type: KEYWORD)
            - 100 messages with 50 fields (one of them 'wheel_model' but not 'Superlight'
            - 100 different values in the rules (no matches with the message field)
        """
        self.routing = Routing()
        my_dict = load_test_data("benchmark_rule_keyword_dict")
        # Create a list of 100 values in the "value" field of the rule
        for i in range(MAX_LIST_VALUES):
            my_dict["filters"][0]["value"].append("test-" + str(i))
        rule = load_test_data("benchmark_rule_keyword")
        # Create 100 EQUALS same rules with 100 values
        for i in range(MAX_RULE):
            rule["streams"]["rules"]["mountain_bike"].append(my_dict)
        self.benchmark_event_1 = load_test_data("benchmark_event_1")
        self.benchmark_event_1.update({"wheel_model": "test"})
        self.routing.load_from_dicts([rule])
        start_time = datetime.now()
        # Sending 100 messages to the routing
        for i in range(MAX_EVENT):
            self.routing.match(self.benchmark_event_1)
        end_time = datetime.now()
        print(f"{self.test3_KEYWORD_list_values.__name__}: {(end_time - start_time).total_seconds()}")

    def test4_KEYWORD_list_values_exists(self):
        """Performance test, for the KEYWORD routing filter type, with:
            - 100 values in the "wheel_model" of the rule and of the message, but none of them triggers a match (no 'Superlight')
        """
        self.routing = Routing()
        my_dict = load_test_data("benchmark_rule_keyword_dict")
        # Create a list of 100 values in the "value" field of the rule
        for i in range(MAX_LIST_VALUES):
            my_dict["filters"][0]["value"].append("test-" + str(i))
        rule = load_test_data("benchmark_rule_keyword")
        # Create 100 EQUALS same rules with 100 values
        for i in range(MAX_RULE):
            rule["streams"]["rules"]["mountain_bike"].append(my_dict)
        self.routing.load_from_dicts([rule])
        # Create a list of values in the message for "wheel_model"
        self.benchmark_event_1 = load_test_data("benchmark_event_1")
        self.benchmark_event_1.update({"wheel_model": []})
        for i in range(MAX_LIST_VALUES):
            self.benchmark_event_1["wheel_model"].append("test-" + str(i))
        start_time = datetime.now()
        # Sending 100 messages to the routing
        for i in range(MAX_EVENT):
            self.routing.match(self.benchmark_event_1)
        end_time = datetime.now()
        print(f"{self.test4_KEYWORD_list_values_exists.__name__}: {(end_time - start_time).total_seconds()}")

def main():
    routing_benchmark = RoutingBenchMark()
    routing_benchmark.test1_EQUALS_no_key_match()
    routing_benchmark.test2_EQUALS_key_exists()
    routing_benchmark.test3_EQUALS_list_values()
    routing_benchmark.test4_EQUALS_list_values_message()
    routing_benchmark.test1_STARTSWITH_no_key_match()
    routing_benchmark.test2_STARTSWITH_key_exists()
    routing_benchmark.test3_STARTSWITH_list_values()
    routing_benchmark.test4_STARTSWITH_list_values_exists()
    routing_benchmark.test1_ENDSWITH_no_key_match()
    routing_benchmark.test2_ENDSWITH_key_exists()
    routing_benchmark.test3_ENDSWITH_list_values()
    routing_benchmark.test4_ENDSWITH_list_values_exists()
    routing_benchmark.test1_KEYWORD_no_key_match()
    routing_benchmark.test2_KEYWORD_key_exists()
    routing_benchmark.test3_KEYWORD_list_values()
    routing_benchmark.test4_KEYWORD_list_values_exists()

if __name__ == "__main__":
    main()
