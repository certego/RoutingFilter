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
 
### Release steps
* (If needed) Update the requirements in `requirements.txt` and `setup.py`
* Add a new entry in `CHANGELOG.md` with the new version number
* Update the version number in `setup.py`
* Commit and merge the changes into `master` branch
* Publish a new release with the version number as a tag: the CI will automatically publish the new version un PyPI

### Benchmark tests
In order to launch the benchmark tests, run ```python routing_benchmark.py```

### Development
* Install `pip install -r requirements.txt` and `pip install -r requirements_dev.txt` in your local virtual environment
* Setup pre-commit: `pre-commit install -c .github/.pre-commit-config.yaml`

### License
This project is licensed under the **GNU LGPLv3** license.