# smonitor Developer Guide — API Sketch

This document defines a minimal public API for `smonitor` and the expected behavior of each entrypoint.

## 1) Public Functions

### configure(...)
Configure the global monitoring behavior.

```python
import smonitor

smonitor.configure(
    level='INFO',
    theme='rich',
    capture_warnings=True,
    trace_depth=3,
    show_traceback=True,
    profile='user',
    handlers=None,
)
```

Parameters
- `level`: global minimum severity for emitting events.
- `theme`: console theme or output style (`'rich'`, `'plain'`).
- `capture_warnings`: intercept `warnings.warn`.
- `trace_depth`: breadcrumb depth to include in output.
- `show_traceback`: include enhanced traceback when errors occur.
- `profile`: output/profile style (`'user'`, `'dev'`, `'qa'`, `'agent'`, `'debug'`).
- `handlers`: optional list of handler instances to override defaults.

Behavior
- Idempotent: calling `configure` multiple times updates the global state.
- If no handlers are provided, a default console handler is created.
- `configure(profile=...)` must override any `_smonitor.py` defaults.

### emit(level, message, *, source=None, extra=None)
Emit a raw diagnostic event.

```python
smonitor.emit('WARNING', 'Selection is ambiguous', source='molsysmt.select')
```
Extended signature (optional fields):
```
emit(level, message, *, source=None, extra=None, category=None, code=None, tags=None)
```

### report()
Return a session report.

```python
summary = smonitor.report()
```

Expected keys
- `calls_total`
- `warnings_total`
- `errors_total`
- `peak_memory` (optional)

## 2) Decorators

### @signal
Wrap a function to automatically push a context frame.

```python
from smonitor import signal

@signal
def my_function(x):
    ...
```

Behavior
- Pushes a breadcrumb frame on entry.
- Pops the frame on exit.
- If an exception is raised, emits an error event and re-raises.

## 3) Configuration Discovery

`_smonitor.py` files can be placed at a project root and auto-loaded by `smonitor.config.discovery`.

Suggested contents:
```python
RULES = {
    'molsysmt.select': {
        'warning_hint': 'Use explicit element selection when possible.'
    }
}
```
Additionally, `_smonitor.py` can define `PROFILE`, `PROFILES`, `ROUTES`, `FILTERS`, `CODES`, and `SIGNALS`.

## 4) Minimal Console Output

Example line format:
```
MOLSYSMT | WARNING | selection.py:42 | Selection string is ambiguous | [molsysmt.select -> arg_digest]
```

## 5) Compatibility and Fallback
- If `smonitor` is not configured, `@signal` should be a near-no-op.
- All bridges (warnings/logging/exceptions) must be reversible.
- Avoid imports of heavy optional dependencies at module top-level.
