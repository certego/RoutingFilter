# RoutingFilter

This is a Python module to handle routing filters based on dictionaries.

### Usage
Load a rule and check whether an event matches the rule or not. 
```
from routingfilter.routing import Routing
routing = Routing()
routing.load_from_dict([test_rule_1])
routing.match(test_event_1)
```
See the [online documentation](https://routingfilter.readthedocs.io/en/latest/) for further details.
 
### License
This project is licensed under the **GNU LGPLv3** license.
