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
    config_path=None,
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
- `config_path`: optional path to a directory or file to load `_smonitor.py` manually.

Behavior
- Idempotent: calling `configure` multiple times updates the global state.
- If no handlers are provided, a default console handler is created.
- `configure(profile=...)` must override any `_smonitor.py` defaults.

### emit(level, message, *, source=None, extra=None, category=None, code=None, tags=None)
Emit a raw diagnostic event.

```python
smonitor.emit('WARNING', 'Selection is ambiguous', source='molsysmt.select')
```

### resolve(message=None, *, code=None, extra=None)
Resolve a message and hint from a code or template without emitting an event.

```python
msg, hint = smonitor.resolve(code='MSM-ERR-001', extra={'arg': 'x'})
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

@signal(tags=["io"], exception_level="ERROR")
def load_file(path):
    ...
```

Parameters
- `tags`: List of strings for categorizing the call (e.g. `["io", "parser"]`).
- `exception_level`: Severity level for exceptions raised within the function (default: `"ERROR"`). Use `"DEBUG"` for exploratory functions that may fail normally.

Behavior
- Pushes a breadcrumb frame on entry.
- Pops the frame on exit.
- If an exception is raised, emits an error event and re-raises.

## 3) Integration Tools

Standard base classes and helpers for library developers (available in `smonitor.integrations`).

### CatalogException & CatalogWarning
Base classes that automatically hydrate messages and hints from a catalog using a `catalog_key`.

### DiagnosticBundle
A container initialized with a catalog, metadata, and package root. It provides `warn`, `warn_once`, and `resolve` helpers tailored for a specific library.

## 4) Configuration Discovery

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
