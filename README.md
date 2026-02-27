# SMonitor


[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/137937243.svg)](https://zenodo.org/badge/latestdoi/137937243)
[![](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/uibcdf/smonitor/actions/workflows/CI.yaml/badge.svg)](https://github.com/uibcdf/smonitor/actions/workflows/CI.yaml)
[![codecov](https://codecov.io/github/uibcdf/smonitor/graph/badge.svg?token=9ZMA4YZLOR)](https://codecov.io/github/uibcdf/smonitor)
[![Install with conda](https://img.shields.io/badge/Install%20with-conda-brightgreen.svg)](https://conda.anaconda.org/uibcdf/smonitor)

*Precision diagnostics for scientific Python ecosystems.*

## Overview

**SMonitor** (Signal Monitor) is a centralized diagnostics and telemetry layer for scientific Python libraries.

It unifies warnings, logging-derived events, exceptions, and execution context into one consistent operational model.

## Why teams adopt SMonitor

- Clear user-facing diagnostics with actionable hints.
- Stable diagnostic contracts (`code`, `signal`) for QA and automation.
- Cross-library traceability with breadcrumb context.
- Local-first reproducibility with bundle export.
- One configuration model across an entire library ecosystem.

## Who it is for

- **Host-library maintainers** integrating diagnostics in package `mylib`.
- **End users** of host libraries who need clearer warnings/errors and rescue guidance.
- **QA and automation teams** validating contracts and machine-readable outputs.

## For AI agents

SMonitor helps agents produce higher-quality diagnosis with lower ambiguity:
- stable machine keys (`code`, `signal`) for deterministic triage,
- profile-specific machine-oriented output (`profile="agent"`),
- local reproducibility artifacts (bundles) for replay and verification.

For safe autonomous workflows:
- keep contracts stable,
- avoid hardcoded diagnostic strings outside catalogs,
- require human review before merging agent-suggested fixes.

## Why SMonitor

- **Single configuration surface** for diagnostics across multiple libraries.
- **Traceability** with breadcrumbs (call-chain context).
- **Profile-aware messaging** (`user`, `dev`, `qa`, `agent`, `debug`).
- **Structured events** for telemetry and tooling.
- **Policy engine** for routing/filtering/transforms.

## Install

```bash
conda install -c uibcdf smonitor
```

## 60-second quick start

```python
import smonitor

smonitor.configure(profile="user", theme="plain")

@smonitor.signal(name="mylib.compute")
def do_work(x):
    if x < 0:
        smonitor.emit(
            "ERROR",
            "Input is invalid.",
            code="MYLIB-E001",
            source="mylib.compute",
            extra={"hint": "Use a non-negative value."},
        )
        return None
    return x * 2

do_work(-1)
```

## Before vs after diagnostics quality

- Less actionable:
  - `ValueError: invalid argument`
- With SMonitor:
  - `ERROR [MYLIB-E001]: Input is invalid. Hint: Use a non-negative value.`

## Core capabilities

- Config precedence: runtime `configure()` > env vars > `_smonitor.py`.
- Catalog-driven diagnostics (`CODES`/`SIGNALS`) for stable contracts.
- Policy engine (`ROUTES`/`FILTERS`) with rate limiting/sampling/transforms.
- Multi-profile output for users, developers, QA, agents, and debug sessions.
- Handlers: console (plain/rich), file, JSON, memory buffer.
- Integration API (`DiagnosticBundle`, `CatalogException`, `CatalogWarning`).
- Event schema checks and strict signal contracts in `dev`/`qa`.
- CLI for validation, checks, report, and bundle export.
- Local bundle export (`bundle.json`, optional `events.jsonl`) for support workflows.
- Profiling features:
  - decorator timing,
  - manual spans,
  - timeline buffering,
  - sampling (`profiling_sample_rate`),
  - timeline export (`json`/`csv`).

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

## Profiling example

```python
from smonitor.profiling import span, export_timeline

smonitor.configure(profiling=True, profiling_sample_rate=1.0)

with span("io.load", path="data.h5"):
    pass

export_timeline("timeline.json", format="json")
```

SMonitor profiling is lightweight observability for library workflows (not a full replacement for dedicated low-level profilers).

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

## Ecosystem adoption

SMonitor integration is complete across:
- MolSysMT
- MolSysViewer
- ArgDigest
- DepDigest
- PyUnitWizard

This makes cross-library diagnostics consistent across the current UIBCDF scientific stack.

## Documentation

- Website: https://www.uibcdf.org/smonitor
- User guide (integrators + end users): `docs/content/user/`
- Developer guide: `devguide/`
- Canonical standards: `standards/`

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

Current release: **0.11.0** (pre-1.0 stabilization).  
Next milestone: **1.0.0** (stable), focused on hardening, API/contract freeze, and sustained CI stability.

## AI Support (Future)

SMonitor is designed to enable opt‑in AI/LLM support workflows:
- structured CODES/SIGNALS for triage,
- local bundles for reproducible diagnosis,
- guarded repair suggestions with human review.

## License

MIT
