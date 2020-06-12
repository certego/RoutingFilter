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

Available filters
==================
For filter types which use "key" and "value" field, they can be both a string or a list of strings.
The chosen logic is OR (at least a match must be satisfied).
* **ALL** - matches with everithing, always returns True
* **EXISTS** - returns True if the key in "key" field exists
* **NOT_EXISTS** - returns False if the key in "key" field exists
* **EQUALS** - returns True if the specified "key" has the given "value"
* **STARTSWITH** - returns True if a "key"'s value starts with "value"
* **KEYWORD** - returns True if "value" is present in "key" (item in list or string in substring)
* **REGEXP** - returns True if a "key"'s value matches the RegExp specified in "value"
* **NETWORK** - Parses the field into ad IP address or network and returns True if the IP address is contained in the specified network
* **NOT_NETWORK** - Parses the field into ad IP address or network and returns True if the IP address is NOT contained in the specified network
* **DOMAIN** - Similar to EQUALS but also tries to parse subdomains (separated by ".")

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