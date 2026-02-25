# Integration Testing Template

Use this page to create a minimal pytest safety net for SMonitor wiring in
library `A`.

## Goal

Detect integration drift early (catalog not loaded, wrong package root,
missing signal fields, broken emitters).

## Minimal test file

Create `tests/test_smonitor_integration.py` in library `A`:

```python
import importlib


def test_library_import_configures_smonitor():
    mod = importlib.import_module("mylib")
    assert mod is not None


def test_catalog_warning_is_emitted():
    from mylib.api import select_atoms
    import smonitor

    smonitor.configure(profile="dev", event_buffer_size=10)
    select_atoms("all")
    events = smonitor.get_manager().recent_events()

    assert events
    last = events[-1]
    assert last["level"] == "WARNING"
    assert last.get("code") == "MYLIB-W001"
    assert "hint" in (last.get("extra") or {})
```

## Optional strict-contract test

```python
def test_strict_signals_contract():
    import smonitor

    smonitor.configure(profile="qa", strict_signals=True)
    # Call a representative API path here and assert no ValueError is raised.
```

## CI smoke command

```bash
pytest -q tests/test_smonitor_integration.py
```

## You are done when

- integration tests fail when wiring breaks,
- diagnostics code/hint contracts are asserted,
- strict QA mode catches missing required fields early.
