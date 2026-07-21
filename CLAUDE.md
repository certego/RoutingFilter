# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`routingfilter` is a Python library ("Generic Business Logic Implementation for Routing objects as python dictionaries") published to PyPI. Given a set of routing rules and an event (both plain `dict`s), it decides which rules an event matches and returns the associated outputs. It is a pure library with no runtime service — the source lives in `routingfilter/` and everything else (tests, benchmark, docs) is tooling around it.

## Common commands

All commands are run from the **repository root** (not from the inner `routingfilter/` package dir) — the test/benchmark code loads fixtures from `test_data/` via relative paths.

```bash
# Install for development
pip install -r requirements.txt -r requirements_dev.txt
pre-commit install -c .github/.pre-commit-config.yaml

# Run the full test suite
pytest routing_test.py

# Run a single test
pytest routing_test.py::RoutingTestCase::test_multiple_rule_loading

# Performance benchmark (not part of the unit tests)
python routing_benchmark.py

# Linting (must pass in CI; configs live under .github/configurations/python_linters/)
black ./routingfilter --config .github/configurations/python_linters/.black --check --diff
flake8 ./routingfilter --config .github/configurations/python_linters/.flake8 --show-source
isort ./routingfilter --sp .github/configurations/python_linters/.isort.cfg --profile black --filter-files --check-only --diff
```

Notes:
- CI (`.github/workflows/python-app.yml`) only runs the build/lint/test job when files under `routingfilter/*` change.
- Line length is 160 across black/flake8/isort.

## Architecture

The matching engine is a strict containment hierarchy. Loading rules builds the tree top-down; matching an event walks it top-down and short-circuits.

```
Routing                     # entry point (routing.py)
 ├─ streams:  Stream        # the "streams" ruleset
 └─ customer: Stream        # the "customers" ruleset
        └─ RuleManager      # one per tag (keyed in Stream._ruleManagers by tag string)
              └─ Rule       # has an output + a list of filters (AND semantics)
                    └─ AbstractFilter subclasses  (filters/filters.py)
```

- **`Routing`** (`routingfilter/routing.py`) is the public API. `load_from_dicts()` / `load_from_jsons()` parse rule configs and instantiate the whole tree; `_get_filters()` is the central factory mapping a filter `type` string (e.g. `"EQUALS"`, `"NETWORK"`) to a concrete filter class. `match(event, type_="streams", tag_field_name="tags")` dispatches to the `streams` or `customer` Stream and returns a `List[Results]`.

- **`Stream`** (`filters/stream.py`) holds `RuleManager`s keyed by tag. On `match()` it reads the event's tags (from `tag_field_name`, default `"tags"`) and invokes only the matching-tag RuleManagers. The special tag **`"all"`** is checked first and short-circuits: if an `all` RuleManager matches, its single result is returned and no other tags are evaluated.

- **`RuleManager`** (`filters/rule.py`) owns an ordered list of `Rule`s for one tag and returns the **first** matching rule (OR / priority-order semantics).

- **`Rule`** (`filters/rule.py`) matches only if **all** its filters match (AND). On a successful match it records the output keys with a timestamp into the event's `certego.routing_history`, which prevents the same output key from being emitted twice across repeated matching. It also tracks per-rule hit stats keyed by the event's `rule.name`.

- **Filters** (`filters/filters.py`) all subclass `AbstractFilter` and implement `match(event) -> bool` plus `_check_value()` (validates/normalizes the configured values, e.g. lowercasing, compiling regexes, parsing IPs; raises `ValueError` on bad config). Available types: `ALL`, `EXISTS`, `NOT_EXISTS`, `EQUALS`, `NOT_EQUALS`, `STARTSWITH`, `ENDSWITH`, `KEYWORD`, `REGEXP`, `NETWORK`, `NOT_NETWORK`, `DOMAIN`, `GREATER`/`LESS`/`GREATER_EQ`/`LESS_EQ` (all `ComparatorFilter`), `TYPEOF`. Most string comparisons are **case-insensitive** (values are lowercased in `_check_value`).

- **`DictQuery`** (`routingfilter/dictquery.py`) is a `dict` subclass whose `get()` walks dotted paths (`"source.ip"`). A literal key containing a `.` is matched before the path is split. This is how filter `key` fields address nested event fields.

- **`Results`** (`filters/results.py`) is the `dataclass` returned for each match (`{rules, output}`). If an output dict contains a `"customer"` key, its value is unwrapped as the output.

### Rule config shape

Rules are dicts nested by stream type → `"rules"` → tag → list of rule objects. Each rule object has a `filters` list, an optional output under the stream-type key, and an optional `id` (a UUID is generated if absent). Example:

```json
{
  "streams": {
    "rules": {
      "my_tag": [
        {
          "filters": [{"type": "EQUALS", "key": "source.ip", "value": "1.2.3.4"}],
          "streams": {"...output..."},
          "id": "optional-id"
        }
      ]
    }
  }
}
```

`load_from_dicts(..., variables={...})` supports variable substitution: filter values that are variable names (referenced with a `$` prefix) are replaced by their configured values before filters are built (`Routing._substitute_variables`).

Extensive real examples of both rules and events live in `test_data/` (`test_rule_*.json`, `test_event_*.json`), which is the best reference when writing or debugging rules.

## Adding a new filter type

1. Add an `AbstractFilter` subclass in `filters/filters.py` implementing `match()` and `_check_value()`.
2. Register its `type` string in the `match` statement of `Routing._get_filters()` (`routing.py`).
3. Add a rule fixture in `test_data/` and a corresponding test case in `routing_test.py`.

## Release process

Update `requirements.txt`/`setup.py` if needed, add a `CHANGELOG.md` entry, bump the version in `setup.py`, merge to `master`, then publish a GitHub release tagged with the version — CI (`python-publish.yml`) publishes to PyPI automatically.