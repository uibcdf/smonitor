# smonitor Developer Guide — API Sketch

This document defines the public API contract for `smonitor` and the expected behavior of each entrypoint.

## 0) Public API Freeze Target (1.0)

Symbols considered public for `1.0.0` stabilization:
- `smonitor.configure`
- `smonitor.emit`
- `smonitor.resolve`
- `smonitor.report`
- `smonitor.signal`
- `smonitor.get_manager`
- `smonitor.export_bundle`
- `smonitor.collect_bundle`
- `smonitor.integrations`

Anything outside this list is internal and may change without compatibility guarantees.

Current status:
- API contract tests exist for top-level exports.
- API contract tests exist for `smonitor.integrations` exports.

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
    silence=['pint', 'networkx'],
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
- `silence`: optional list of logger names (or prefixes) to ignore completely.

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

### Probing Semantics
Exploratory predicates (`is_form`, `is_item`, `is_quantity`, `is_unit`) should
emit expected misses at `DEBUG` level only.

- Expected probe miss: `DEBUG` (telemetry), typically with a code/tag such as
  `*-DBG-PROBE-*`.
- Recoverable anomaly requiring user attention: `WARNING`.
- Operation failure that prevents requested output: `ERROR`.

In `user` profile, expected probe misses should not be surfaced as actionable
errors.

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


## Profiling-oriented signal options

`@signal` now supports optional profiling-oriented context:

- `tags=[...]` to classify calls in timeline/report outputs,
- `extra_factory=...` to attach structured per-call context to timeline entries and derived events,
- opt-in slow-signal events when `slow_signal_ms` is configured.
- Human-readable handlers (`console`, `file`) may truncate large structured payload fragments for `qa`, `dev`, and `debug` profiles. This does not alter the routed event payload or JSON handler output.

- `smonitor.integrations.context_extra(...)` builds stable structured payloads for common diagnostic fields without repeating the same key assembly in each library.
- `context_extra(...)` also reserves canonical retry/causal fields for cross-library QA payloads: `retry_attempt`, `retry_max`, `retry_exhausted`, `retry_delay_s`, `failure_class`, `last_failure_reason`, `cause_exception_type`, `cause_code`, and `causal_chain`.

- `report()` now includes `events_by_code`, `events_by_category`, and `slow_signals_recent` to support QA triage without scanning raw event streams.
- Bundle exports mirror this information under `triage`.

- Repeated transient warnings can be coalesced with `warning_coalesce_window_s`; suppressed duplicates are summarized in `report()` and bundle triage output.
- Coalesced warning windows also emit a final summary event (`SMONITOR-WARNING-COALESCED`) when the window is finalized so CI/event streams can retain the aggregate retry outcome.

- `JsonHandler` now emits a `normalized` payload section with stable machine-oriented fields (`level`, `message`, `source`, `code`, `category`, `exception_type`, `tags`, plus selected structured-context keys).
- The normalized payload now promotes canonical retry/causal keys as first-class machine-readable fields.
