# Architecture

SMonitor is organized around five layers:
- `core`: manager, context, decorator
- `emitters`: warnings/logging/exceptions capture
- `handlers`: console/file/json/memory outputs
- `policy`: routing/filtering/transforms
- `integrations`: helpers for ecosystem packages

## Core design decisions

- One global manager controls runtime behavior.
- Libraries configure SMonitor through `_smonitor.py` and `ensure_configured`.
- Diagnostics are catalog-driven (codes/signals), not hardcoded strings.
- Handlers are isolated so failures do not crash scientific workflows.

## Architectural invariants

- Runtime precedence: `configure()` > env vars > `_smonitor.py`.
- User-facing messages must remain explicit and actionable.
- Emission failures must never be silently swallowed.
