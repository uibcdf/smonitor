# smonitor

**smonitor** is a centralized diagnostic and telemetry system for the scientific Python stack.  
It unifies logs, warnings, errors, and execution context across an ecosystem of libraries.

## Why smonitor

- **Single configuration surface** for diagnostics across multiple libraries.
- **Traceability** with breadcrumbs (call-chain context).
- **Profile-aware messaging** (`user`, `dev`, `qa`, `agent`, `debug`).
- **Structured events** for telemetry and tooling.
- **Policy engine** for routing/filtering.

## Quick Start

```python
import smonitor

smonitor.configure(profile="user", theme="plain")

@smonitor.signal
def do_work(x):
    if x < 0:
        raise ValueError("x must be >= 0")
    return x * 2

do_work(3)
```

## Configuration

Project-wide configuration is read from `_smonitor.py` at the repo root. Runtime
`configure()` always overrides project defaults.

```python
# _smonitor.py
PROFILE = "user"

SMONITOR = {
    "level": "WARNING",
    "trace_depth": 3,
    "capture_warnings": True,
    "capture_logging": True,
    "theme": "plain",
}

CODES = {
    "MSM-W010": {
        "title": "Selection ambiguous",
        "user_message": "La selección '{selection}' es ambigua.",
        "user_hint": "Especifica la selección con más detalle (ejemplo: {example}).",
    }
}
```

## Profiling

Enable lightweight profiling with `profiling=True`. It records durations per
`@signal` and aggregates stats in `report()`. You can also use spans and export
timelines:

```python
from smonitor.profiling import span, export_timeline

smonitor.configure(profiling=True, profiling_sample_rate=1.0)

with span("io.load", path="data.h5"):
    pass

export_timeline("timeline.json", format="json")
```

## Policy Engine

Use `ROUTES` and `FILTERS` in `_smonitor.py` to route or filter events.

```python
ROUTES = [
  {"when": {"level": "WARNING"}, "send_to": ["console", "json"]}
]

FILTERS = [
  {"when": {"code": "MSM-W010"}, "rate_limit": "1/100@60"}
]
```

## CLI

```bash
smonitor --validate-config
smonitor --check
smonitor --check --check-event '{"level":"WARNING","message":"x"}'
```

## Development

```bash
pytest
ruff check .
```

Docs build:
```bash
make -C docs html
```

## Status

Current release: **0.1.0** (early, foundational).  
Integration with ecosystem libraries is planned for the 1.0 release.

## License

MIT
