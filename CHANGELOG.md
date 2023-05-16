## 1.4.x
### 1.4.0
#### Features
* Added filters: IS_STR, IS_INT, IS_BOOL; IS_LIST, IS_DICT, TYPEOF
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