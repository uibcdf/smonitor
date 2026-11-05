# Library Integration Contract

This showcase targets developers integrating SMonitor into a host library.

## Problem

You want consistent diagnostics across your package without scattering custom
hardcoded monitoring logic across modules.

## Pattern

Define configuration in `mylib/_smonitor.py`, define contracts in
`mylib/_private/smonitor/`, and instrument API boundaries with `@signal`.

```python
# mylib/_smonitor.py
CONFIG = {
    "profile": "user",
    "theme": "rich",
    "strict_signals": True,
    "strict_schema": True,
}
```

```python
# mylib/_private/smonitor/catalog.py
CODES = {
    "MYLIB-W001": {
        "level": "WARNING",
        "message": "Selection is ambiguous.",
        "hint": "Use a more specific selector.",
    }
}

SIGNALS = {
    "mylib.select": {"codes": ["MYLIB-W001"]},
}
```

```python
# A/select.py
import smonitor

@smonitor.signal(name="mylib.select")
def select(items, query):
    if query == "all":
        smonitor.emit(
            "WARNING",
            "Selection is ambiguous.",
            code="MYLIB-W001",
            source="mylib.select",
        )
```

## Why this works

- contract and behavior stay centralized;
- diagnostics are stable for users, QA, and automation;
- each emitted event carries reusable metadata.

## Where to apply

- public API entrypoints;
- data conversion boundaries;
- optional backend selection paths.
