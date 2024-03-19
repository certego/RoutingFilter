## 2.3.x
### 2.3.3
#### Changes
* Bumped package version to match tag
### 2.3.0
#### Changes
* Added multiple variables management
#### Bugfix
* Fixed bug in equal filter about upper and lower case
## 2.2.x
### 2.2.9
#### Bugfix
* Fixed customer routing history
#### Changes
* Updated _check_value() method in filters
### 2.2.8
#### Bugfix
* Fixed a bug when an existing fields didn't match
### 2.2.7
#### Bugfix
* Fixed bug in exist filter
### 2.2.6
#### Bugfix
* Removed error logging in *filters.py*
### 2.2.5
#### Bugfix
* Fixed version in *setup.py*
### 2.2.4
#### Bugfix
* Removed warning logging in *\_substitute_variables*
### 2.2.3
#### Bugfix
* Fixed rule get_stats 
### 2.2.2
#### Bugfix
* Fixed result output
* Fixed customer stream type
* Fixed equal filter
### 2.2.1
#### Bugfix
* Fixed bug in *match()* method of *Routing* class
### 2.2.0
#### Features
* Added *to_dict()* method to Results class
#### Changes
* Updated *setup.py*

## 2.1.x
### 2.1.0
#### Features
* Added count method in Routing

## 2.0.x
### 2.0.0
#### Changes
* Refactoring of Routing Filter Class (object-oriented)

## 1.6.x
### 1.6.3
#### Bugfix
* Fix overwriting of certego field
### 1.6.2
#### Bugfix
* Added filter in routing_filter
### 1.6.1
#### Bugfix
* Fixed TypeError if output is None
* Fixed routing_history with double tag and double streams
### 1.6.0
#### Features
* Added keyword replacement in case of rule with list variables

## 1.5.x
### 1.5.2
#### Changes
* Fixed test4 (with list in rule value and also in the event) in routing_benchmark that matched with the rules
### 1.5.1
#### Changes
* Updated setup.py
### 1.5.0
#### Features
* Added routing history and loop protection in rule parsing

## 1.4.x
### 1.4.1+
#### Bugfix
* Updated *setup.py* to include new dependency *macaddress* 
### 1.4.0
#### Features
* Added filter TYPEOF in order to check if the target is a str, int, bool, list, dict, ip address or mac address
* Implemented the use of variables in filter values

## 1.3.x
### 1.3.2
### Bugfix
* Fixed another crash in NETWORK filter when an unparsable network/IP is passed and enhanced related logging
### 1.3.1
### Bugfix
* Fixed crash in NETWORK filter when an unparsable network/IP is passed
### 1.3.0
### Features
* Implemented NOT_EQUAL filter
#### Bugfix
* Fixed a bug in NOT_NETWORK filter

## 1.2.x
### 1.2.1
#### Bugfix
* Fixed a DictQuery bug
### 1.2.0
#### Features
* Implemented ENDSWITH filter

## 1.1.x
### 1.1.7
#### Bugfix
* Fixed routing matching when source key is a list.
### 1.1.6
#### Bugfix
* Fixed missing rule output when matching a rule with "all" special tag
### 1.1.5
#### Bugfix
* Added a break in "all" special tag processing
### 1.1.4
#### Bugfix
* Fixed a bug in rules loading with deepcopy
### 1.1.3
#### Bugfix
* Fixed a bug DictQuery
### 1.1.2
#### Bugfix
* Fixed a bug in NETWORK filter type processing
### 1.1.1
#### Features
* Added some logging
#### Bugfix
* Fixed a bug in GREATER, LESS, GREATER_EQ, LESS_EQ processing
#### Changes
* Added rule validation when loading rules_list (this can be disabled)
* An exception is returned (instead of False) when processing a wrong filter type
### 1.1.0
#### Changes
* Changed match output to to list of dicts, to allow multiple rules with different tags to match
* Now the method laod_from_dicts returns nothing; a new getter has been added to retrieve the currently loaded rules

## 1.0.x
### 1.0.0
* First release