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
        self.routing = Routing()
        my_dict = load_test_data("benchmark_rule_dict")
        rule = load_test_data("benchmark_rule_1_equals")
        for i in range(MAX_RULE):
            rule["streams"]["rules"]["mountain_bike"].append(my_dict)
        self.benchmark_event_1_equal = load_test_data("benchmark_event_1_equal")
        self.routing.load_from_dicts([rule])
        start_time = datetime.now()
        for i in range(MAX_EVENT):
            self.routing.match(self.benchmark_event_1_equal)
        end_time = datetime.now()
        print(f"{self.test1_EQUALS_no_key_match.__name__}: {(end_time - start_time).total_seconds()}")

    def test2_EQUALS_key_exists(self):
        self.routing = Routing()
        my_dict = load_test_data("benchmark_rule_dict")
        rule = load_test_data("benchmark_rule_1_equals")
        for i in range(MAX_RULE):
            rule["streams"]["rules"]["mountain_bike"].append(my_dict)
        self.benchmark_event_1_equal = load_test_data("benchmark_event_1_equal")
        self.benchmark_event_1_equal.update({"wheel_model": "test"})
        self.routing.load_from_dicts([rule])
        start_time = datetime.now()
        for i in range(MAX_EVENT):
            self.routing.match(self.benchmark_event_1_equal)
        end_time = datetime.now()
        print(f"{self.test2_EQUALS_key_exists.__name__}: {(end_time - start_time).total_seconds()}")
    
    def test3_EQUALS_list_values(self):
        self.routing = Routing()
        my_dict = load_test_data("benchmark_rule_dict")
        rule = load_test_data("benchmark_rule_1_equals")
        for i in range(MAX_RULE):
            rule["streams"]["rules"]["mountain_bike"].append(my_dict)
        for i in rule["streams"]["rules"]["mountain_bike"]:
            for j in range(MAX_LIST_VALUES):
                i["filters"][0]["value"].append("test-" + str(j))
        self.benchmark_event_1_equal = load_test_data("benchmark_event_1_equal")
        self.benchmark_event_1_equal.update({"wheel_model": "test"})
        self.routing.load_from_dicts([rule])
        start_time = datetime.now()
        for i in range(MAX_EVENT):
            self.routing.match(self.benchmark_event_1_equal)
        end_time = datetime.now()
        print(f"{self.test3_EQUALS_list_values.__name__}: {(end_time - start_time).total_seconds()}")

def main():
    routing_benchmark = RoutingBenchMark()
    routing_benchmark.test1_EQUALS_no_key_match()
    routing_benchmark.test2_EQUALS_key_exists()
    routing_benchmark.test3_EQUALS_list_values()

if __name__ == "__main__":
    main()