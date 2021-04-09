## 1.0.x
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

### 1.0.0
* First release