# Mini Library Walkthrough

This chapter gives you a complete integration narrative using a fictional package: `mylib`.

## Scenario

You maintain `mylib`, a scientific package with optional capabilities. You want:
- clear diagnostics for end users,
- low-noise telemetry for developers,
- predictable integration behavior.

## Target structure

```text
mylib/
  __init__.py
  _smonitor.py
  _private/
    smonitor/
      __init__.py
      catalog.py
      meta.py
      emitter.py
      exceptions.py
      warnings.py
  core/
    analysis.py
```

## Step 1. Define project metadata

Create `mylib/_private/smonitor/meta.py`:

```python
META = {
    "library": "mylib",
    "docs_url": "https://example.org/mylib/docs",
    "issues_url": "https://github.com/org/mylib/issues",
    "api_url": "https://example.org/mylib/api",
}
```

## Step 2. Define catalog and contracts

Create `mylib/_private/smonitor/catalog.py`:

```python
CATALOG = {
    "codes": {
        "MYLIB-E101": {
            "title": "Invalid argument format",
            "user_message": "Argument '{argument}' has invalid format: {value}.",
            "user_hint": "Use format '{expected}'.",
            "dev_message": "Invalid argument format in {function}.",
            "dev_hint": "Validate parser and normalization rules.",
        }
    },
    "signals": {
        "mylib.core.analysis.run": {
            "extra_required": ["argument", "value", "expected"],
            "errors": ["MYLIB-E101"],
        }
    },
}
```

## Step 3. Wire bundle helpers

Create `mylib/_private/smonitor/__init__.py`:

```python
from pathlib import Path

from .catalog import CATALOG
from .meta import META

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
```

Create `mylib/_private/smonitor/emitter.py`:

```python
from smonitor.integrations import DiagnosticBundle

from . import CATALOG, META, PACKAGE_ROOT

bundle = DiagnosticBundle(CATALOG, META, PACKAGE_ROOT)
warn = bundle.warn
warn_once = bundle.warn_once
resolve = bundle.resolve
```

## Step 4. Use catalog-based exceptions

Create `mylib/_private/smonitor/exceptions.py`:

```python
from smonitor.integrations import CatalogException

from . import CATALOG, META


class MyLibException(CatalogException):
    def __init__(self, **kwargs):
        super().__init__(catalog=CATALOG, meta=META, **kwargs)


class InvalidArgumentFormat(MyLibException):
    catalog_key = "MYLIB-E101"
```

## Step 5. Instrument and raise

```python
from smonitor import signal

from mylib._private.smonitor.exceptions import InvalidArgumentFormat


@signal(tags=["analysis"])
def run(argument: str, value: str):
    if not value.startswith("A:"):
        raise InvalidArgumentFormat(
            extra={
                "argument": argument,
                "value": value,
                "expected": "A:<token>",
                "function": "mylib.core.analysis.run",
            }
        )
```

## Step 6. Verify behavior

Test at least these cases:
- valid input runs without warnings,
- invalid input raises your catalog-based exception,
- exception message is explicit in `user` profile,
- diagnostics include enough context in `dev` profile.

## Why this pattern scales

This layout separates concerns cleanly:
- scientific logic remains clean,
- message contracts live in catalog,
- profile-dependent presentation stays in SMonitor.

## Next

Continue with [Configuration](configuration.md) to control profile, policy, and precedence.
