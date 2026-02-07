# smonitor Developer Guide

## Purpose
`smonitor` centralizes logs, warnings, errors, and telemetry across the UIBCDF ecosystem. It provides a single configuration surface, a consistent event model, and rich, traceable output for developers and users.

## Design Goals
- Single point of configuration for diagnostics across sibling libraries.
- Traceability via a call-chain context (breadcrumbs).
- Rich, human-friendly output with optional structured logs.
- Symmetry with `arg_digest` and `dep_digest` through a `@signal` decorator.
- Zero-surprise behavior: opt-in with graceful fallback when disabled.
- Configuration discovery via `_smonitor.py` in project roots.
- Policy-driven routing and filtering of events (Policy Engine).
- Profile-based communication styles (user/dev/qa/agent/debug).

## Architecture Overview
```
smonitor/
  core/
    manager.py      # Global engine (singleton dispatcher)
    decorator.py    # @signal decorator
    context.py      # Context stack + breadcrumb metadata
  emitters/
    log.py          # Logging bridge
    warn.py         # warnings bridge
    error.py        # exception bridge
  handlers/
    console.py      # Rich terminal output
    file.py         # Text file output
    json.py         # Structured output
  config/
    discovery.py    # Auto-load _smonitor.py rules
  policy/
    engine.py       # Policy Engine (routing/filtering/transforms)
```

## Event Model
All events emitted by smonitor should normalize to a single payload shape:
- `level`: INFO, WARNING, ERROR, DEBUG
- `source`: library or module name
- `message`: human-readable text
- `context`: call-chain and metadata from `context.py`
- `extra`: structured dict for domain-specific data
Optional fields:
- `category`, `code`, `library`, `exception_type`, `event_id`, `tags`

## Core Components

### 1) core.manager
Singleton responsible for:
- runtime configuration state
- registering handlers
- routing events to handlers
- holding the active context stack
- evaluating policy rules and profiles

### 2) core.context
- Uses `contextvars` to store a per-task call-chain
- Each frame contains: function name, module, args summary (optional), timestamp
- Push/pop occurs via `@signal`

### 3) core.decorator (@signal)
- Wraps a function, pushing a context frame at entry and popping on exit
- Captures exceptions and emits error signals before re-raising
- Provides minimal overhead when smonitor is disabled

## Emitters

### warnings bridge (emitters.warn)
- Override `warnings.showwarning` when enabled
- Convert warnings into smonitor events

### logging bridge (emitters.log)
- Provide a `logging.Handler` or `LoggerAdapter`
- Ensure standard logging funnels into smonitor events

### exception bridge (emitters.error)
- Optional `sys.excepthook` integration for unhandled exceptions
- Attach call-chain context for top-level crashes
 
## Policy Engine
- Declarative routing/filtering/transforms applied after normalization and before handler dispatch.
- Uses `when` matchers on event fields (level/source/code/category/tags/etc.).
 
## Profiles
- Profiles define communication style: `user`, `dev`, `qa`, `agent`, `debug`.
- Runtime `configure(profile=...)` overrides environment variables and `_smonitor.py`.

## Handlers

### Handler Priority
The core visual experience is now anchored by an exceptional `RichConsoleHandler`. The manager is capable of automatic handler selection based on environment and requested theme.

### console handler
- **Exceptional Rich Handler**: Uses `rich` for elegant panels (user profile) and structured audit reports (dev/qa/debug profiles). Includes icon-driven gravity indicators and call-chain breadcrumbs.
- Fallback plain formatting when `rich` is unavailable.

### file handler
- Plain-text logs, optionally JSON lines
- Rotation is external or optional

### json handler
- Structured event output for telemetry or external ingestion

## Configuration API

### Project Configuration Location
The project configuration file (`_smonitor.py`) must always reside in the package root (e.g., `molsysmt/_smonitor.py`). Configurations in submodules are not permitted to ensure a single source of truth per library.

### configure(...)
Expected API signature:
```
smonitor.configure(
    level='INFO',
    theme='rich',
    capture_warnings=True,
    trace_depth=3,
    show_traceback=True
)
```

### report()
- Returns a diagnostic summary of the session
- Counts calls, warnings, errors, and optional performance metrics

## Integration Strategy

### Phase 1: Core MVP
- Implement manager, context, decorator
- Basic console handler
- Simple warning/logging bridges

### Phase 2: Ecosystem integration
- Add `@signal` to key entrypoints in arg_digest and dep_digest
- Provide `_smonitor.py` in each library to customize hints and formatting

### Phase 3: MolSysMT adoption
- Replace `msm.config.setup_logging()` with `smonitor.configure()`
- Ensure deprecation warnings route through smonitor

### Phase 4: Documentation
- Auto-generate tables of monitored functions
- Provide examples and best practices

## Compatibility Notes
- If smonitor is not configured, `@signal` should be a near-no-op.
- Avoid importing optional dependencies at top-level.
- Keep event payloads stable for tooling and tests.

## Suggested Development Checklist
- [x] Implement core manager and context stack
- [x] Implement @signal decorator
- [x] Implement warnings bridge
- [x] Implement logging bridge
- [x] Add exceptional console handler with rich
- [x] Add file and json handlers
- [x] Write smoke tests for context propagation
- [x] Integrate with dep_digest and arg_digest
- [ ] Add docs and usage examples
