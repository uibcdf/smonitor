# Configuration

This page explains how SMonitor decides effective behavior in your library.

## The model

Configuration can come from three places:
1. runtime calls (`smonitor.configure(...)`),
2. environment variables,
3. `_smonitor.py` in package root.

Priority is strict:

1. Runtime `configure()`
2. Environment variables
3. `_smonitor.py`

This lets your library provide safe defaults while still allowing developers and QA to override behavior explicitly.

## Recommended `_smonitor.py`

```python
PROFILE = "user"

SMONITOR = {
    "level": "WARNING",
    "trace_depth": 3,
    "capture_warnings": True,
    "capture_logging": True,
    "capture_exceptions": False,
    "show_traceback": False,
    "profiling": False,
    "strict_signals": False,
    "strict_schema": False,
    "event_buffer_size": 500,
    "handler_error_threshold": 5,
}

PROFILES = {
    "user": {"level": "WARNING", "show_traceback": False},
    "dev": {"level": "INFO", "show_traceback": True},
    "qa": {"level": "INFO", "show_traceback": True},
    "agent": {"level": "WARNING", "show_traceback": False},
    "debug": {"level": "DEBUG", "show_traceback": True},
}

ROUTES = [
    {"when": {"level": "ERROR"}, "send_to": ["console", "json"]},
]

FILTERS = [
    {"when": {"code": "MYLIB-W001"}, "rate_limit": "1/100@60"},
]
```

## Environment variables you will actually use

Common toggles during development:
- `SMONITOR_PROFILE`
- `SMONITOR_LEVEL`
- `SMONITOR_CAPTURE_WARNINGS`
- `SMONITOR_CAPTURE_LOGGING`
- `SMONITOR_STRICT_SIGNALS`
- `SMONITOR_STRICT_SCHEMA`
- `SMONITOR_EVENT_BUFFER`

## Practical advice

- Keep `_smonitor.py` defaults conservative (`user` profile).
- Use runtime overrides in tests and CI (`dev` or `qa`).
- Use `strict_signals` in QA to catch catalog-contract drift early.
- Use rate limits for known repetitive warnings.

## Configuration anti-patterns

Do not:
- hardcode warning strings in scientific modules,
- duplicate template definitions in multiple files,
- use `except Exception: pass` around diagnostics emission.

## Next

Continue with [Integrating Your Library](integrating-your-library.md) for migration strategy in an existing codebase.
