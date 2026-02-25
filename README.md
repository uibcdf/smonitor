# SMonitor

**SMonitor** (Signal Monitor) is a centralized diagnostic and telemetry system for the scientific Python stack.  
It unifies logs, warnings, errors, and execution context across an ecosystem of libraries.

## Why SMonitor

- **Single configuration surface** for diagnostics across multiple libraries.
- **Traceability** with breadcrumbs (call-chain context).
- **Profile-aware messaging** (`user`, `dev`, `qa`, `agent`, `debug`).
- **Structured events** for telemetry and tooling.
- **Policy engine** for routing/filtering/transforms.

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

Project-wide configuration is read from `_smonitor.py` at the **package root**.
Precedence is: runtime `configure()` > environment variables > `_smonitor.py`.

```python
# _smonitor.py (package root)
PROFILE = "user"

SMONITOR = {
    "level": "WARNING",
    "trace_depth": 3,
    "capture_warnings": True,
    "capture_logging": True,
    "theme": "plain",
    "strict_config": False,
}

CODES = {
    "MSM-W010": {
        "title": "Selection ambiguous",
        "user_message": "Selection {selection} is ambiguous.",
        "user_hint": "Use a more specific selection (example: {example}).",
    }
}
```

## Package Catalogs

Libraries can keep their diagnostics catalog in `mylib/_private/smonitor/catalog.py`
(CODES/SIGNALS + metadata) and call `smonitor.integrations.emit_from_catalog(...)`
to emit structured events.

## Canonical Guide

The canonical integration guide is `standards/SMONITOR_GUIDE.md`. Use it as the
source of truth and sync it to sibling repos with:

```bash
python devtools/sync_smonitor_guide.py
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

## Bundles

Generate a local diagnostics bundle for reproducible troubleshooting:

```bash
smonitor export --out smonitor_bundle --max-events 500
```

This creates `bundle.json` and `events.jsonl` (if buffering is enabled).

## Policy Engine

Use `ROUTES` and `FILTERS` in `_smonitor.py` to route or filter events.

```python
ROUTES = [
  {"when": {"level": "WARNING"}, "send_to": ["console", "json"]}
]

FILTERS = [
  {"when": {"code": "MSM-W010"}, "rate_limit": "1/100@60"},
  {"when": {"level": "INFO"}, "sample": 0.1}
]
```

## CLI

```bash
smonitor --validate-config
smonitor --check
smonitor --check --check-event level:WARNING
smonitor export --out smonitor_bundle --max-events 500
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

Current release: **0.10.0** (feature complete, hardening phase).  
Ecosystem integration is **complete** (MolSysMT, MolSysViewer, ArgDigest, DepDigest, PyUnitWizard).

Next milestone: **0.11.0** (pre-1.0 stabilization):
- finalize docs and examples,
- confirm test environments and release gates,
- stabilize public API surface.

## AI Support (Future)

SMonitor is designed to enable opt‑in AI/LLM support workflows:
- structured CODES/SIGNALS for triage,
- local bundles for reproducible diagnosis,
- guarded repair suggestions with human review.

## License

MIT
