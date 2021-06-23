.. RoutingFilter documentation master file, created by
   sphinx-quickstart on Wed Jun 10 17:44:32 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to RoutingFilter's documentation!
=========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Usage
==================
Sample usage::

   from routingfilter.routing import Routing

   test_event_1 = {
       "tags": "mountain_bike",
       "wheel_model": "Superlight",
       "frame": "aluminium",
       "gears": "1x12",
       "suspension": "full"
   }

   test_rule_1 = {
       "streams": {
           "rules": {
               "mountain_bike": [
                   {
                       "filters": [
                           {
                               "type": "EQUALS",
                               "key": "wheel_model",
                               "description": "Carbon fiber wheels needs manual truing",
                               "value": ["Superlight", "RacePro"]
                           }
                       ],
                       "streams": {
                           "Workshop": {
                               "workers_needed": 1
                           }
                       }
                   }
               ]
           }
       }
   }

   routing = Routing()
   routing.load_from_dict([test_rule_1])
   routing.match(test_event_1)

The rule's top level name (default `streams`) can be changed. In this case, the new name can be specified when calling the `match` method.

At the moment, the second level (`rule`) is hard-coded and will likely be removed in the future, since it has no semantic.

The third level matches a field in the event (default `tags`). It can be changed when calling the `matches` method.
When the first rule with a given tag (i.e. "mountain_bike") matches the event, the following are ignored.
Rules with different tags can match independently (for example, if we want to send an event to different pipelines, based on the tag).

The "streams" element after `filters` means that, if the filter matches, the event will be enriched with the `Workshop` dictionary.

Available filters
==================
For filter types which use "key" and "value" field, they can be both a string or a list of strings.
The chosen logic is OR (at least a match must be satisfied).

* **ALL** - matches with everithing, always returns True (if this matches, all other rules are ignored)
* **EXISTS** - returns True if the key in "key" field exists
* **NOT_EXISTS** - returns False if the key in "key" field exists
* **EQUALS** - returns True if the value in the specified "key" is equal to "value"
* **STARTSWITH** - returns True if a "key"'s value starts with "value"
* **ENDSWITH** - returns True if a "key"'s value ends with "value"
* **KEYWORD** - returns True if "value" is present in "key" (item in list or string in substring)
* **REGEXP** - returns True if a "key"'s value matches the RegExp specified in "value"
* **NETWORK** - Parses the field into ad IP address or network and returns True if the IP address is contained in the specified network
* **NOT_NETWORK** - Parses the field into ad IP address or network and returns True if the IP address is NOT contained in the specified network
* **DOMAIN** - Similar to EQUALS but also tries to parse subdomains (separated by ".")
* **GREATER** - returns True if the value in the specified "key" is greater than "value".
* **LESS** - returns True if the value in the specified "key" is less than "value"
* **GREATER_EQ** - returns True if the value in the specified "key" is greater than or equal to "value"
* **LESS_EQ** - returns True if the value in the specified "key" is less than or equal to "value"

The filters NETWORK and NOT_NETWORK must be strings containing a valid IP or network address (using CIDR notation), otherwise a ValueError is raised.
The filters GREATER, LESS, GREATER_EQ, LESS_EQ require float (or float-parsable) values, otherwise a ValueError is raised.

Example
==================
Let's see a routing application with firewall rules. We have network traffic events in the following format: ::

   test_event_n1 = {
     "tags": "ip_traffic",
     "src_addr": "192.168.1.10",
     "dst_addr": "192.168.1.15",
     "domain": "test.domain.local"
   }
   test_event_n2 = {
     "tags": "ip_traffic",
     "src_addr": "192.168.2.10",
     "dst_addr": "192.168.2.15",
     "domain": "test.otherdomain.local"
   }

We want to filter all traffic tagged as `ip_traffic`, coming from the subnet `192.168.1.0/24` and enrich all the other events with a new field `processed`.
We create the following rule: ::

   test_rule_n1 = {
     "streams": {
       "rules": {
         "ip_traffic": [
           {
             "filters": [
               {
                 "type": "NETWORK",
                 "key": "src_addr",
                 "value": "192.168.1.0/24"
               }
             ],
             "streams": {
               "filtered": False
             }
           }
         ]
       }
     }
   }

If we apply this rule to `test_event_n1`, it will match, since the `src_addr` is in the subnet `192.168.1.0/24`. We are obtaining the following output: ::

   {
     "rules": [
       {
         "type": "NETWORK",
         "key": "src_addr",
         "value": "192.168.1.0/24"
       }
     ],
     "output": {
       "filtered": False
     }
   }

The second event will not match with rule `test_event_n1`, since the `src_addr` is not in the subnet `192.168.1.0/24`. The function will return an empty dictionary.

Routing
==================
.. automodule:: routingfilter.routing
   :members:
   :undoc-members:
   :show-inheritance:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`