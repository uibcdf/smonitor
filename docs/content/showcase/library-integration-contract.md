# Library Integration Contract

This showcase targets developers integrating SMonitor into library `A`.

## Problem

You want consistent diagnostics across your package without scattering custom
hardcoded monitoring logic across modules.

## Pattern

Define configuration in `A/_smonitor.py`, define contracts in
`A/_private/smonitor/`, and instrument API boundaries with `@signal`.

```python
# A/_smonitor.py
CONFIG = {
    "profile": "user",
    "theme": "rich",
    "strict_signals": True,
    "strict_schema": True,
}
```

```python
# A/_private/smonitor/catalog.py
CODES = {
    "A-W001": {
        "level": "WARNING",
        "message": "Selection is ambiguous.",
        "hint": "Use a more specific selector.",
    }
}

SIGNALS = {
    "A.select": {"codes": ["A-W001"]},
}
```

```python
# A/select.py
import smonitor

@smonitor.signal(name="A.select")
def select(items, query):
    if query == "all":
        smonitor.emit(
            "WARNING",
            "Selection is ambiguous.",
            code="A-W001",
            source="A.select",
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
