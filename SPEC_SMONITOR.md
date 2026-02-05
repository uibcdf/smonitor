# SPEC_SMONITOR.md — Centralized Diagnostic & Telemetry System

**Version:** v0.1 (Draft)  
**Status:** CONCEPT  
**Author:** UIBCDF Development Team  
**Project Name:** `monitor`

## 1. Motivation & Vision

Currently, the UIBCDF ecosystem (MolSysMT, TopoMT, ArgDigest, DepDigest, PyUnitWizard) operates as a collection of independent modules. While each handles its own logging, warnings, and errors, the resulting output is often fragmented, redundant, or lacks global context.

**Monitor** is designed to be the **Central Nervous System** of the suite. Its mission is to capture, coordinate, and present all internal events (logs, warnings, exceptions, and telemetry) in a unified, traceable, and user-friendly manner.

### Core Goals:
1.  **Orchestration**: Provide a single point of configuration for the diagnostic behavior of all sibling libraries.
2.  **Traceability**: Maintain a "call-chain" context (e.g., knowing that an error in `PyUnitWizard` originated from an `@arg_digest` call inside `msm.convert`).
3.  **Aesthetics & Clarity**: Leverage modern terminal formatting (like `rich`) to produce beautiful, readable, and informative reports.
4.  **Symmetry**: Follow the design patterns established by `arg_digest` and `dep_digest` for developer familiarity.

---

## 2. Architecture

The library is structured into four main layers:

```
monitor/
  core/
    manager.py      # The global engine (Singleton dispatcher)
    decorator.py    # The @signal decorator logic
    context.py      # Call-stack and execution metadata (The Breadcrumbs)
  emitters/
    log.py          # Integration with Python's standard logging
    warn.py         # Interceptor for warnings.warn()
    error.py        # Exception enhancement and coordination logic
  handlers/
    console.py      # Rich terminal output (colors, tables, source code)
    file.py         # Standard logging output to disk
    json.py         # Structured data for automated audits and telemetry
  config/
    discovery.py    # Auto-resolves _smonitor.py in project roots
```

---

## 3. Public API

### 3.1 The `@signal` Decorator
The primary way to connect a function to the diagnostic system.

```python
from smonitor import signal

@signal
def my_function(item, selection='all'):
    # This function is now monitored. 
    # Any log, warning, or error inside (even in dependencies) will be tagged with this context.
    ...
```

### 3.2 Global Configuration
A single call to rule them all.

```python
import smonitor

smonitor.configure(
    level='INFO',          # Global verbosity
    theme='rich',          # Use colors, tables, and enhanced formatting
    capture_warnings=True, # Intercept all warnings.warn()
    trace_depth=3,         # How many levels of parent-calls to show
    show_traceback=True,   # Enhanced error context
    profile='user',        # Output profile: user/dev/qa/agent/debug
    profiling=False        # Attach duration to context frames
)
```

---

## 4. Key Features

### 4.1 Nested Traceability (The "Breadcrumb" Trail)
When an event occurs, `monitor` reports the path of execution:
`[molsysmt.convert] -> [arg_digest] -> [pyunitwizard] | ERROR: Invalid Unit`

### 4.2 Standardized Warning Redirection
Instead of messy Python warnings, `monitor` intercepts them and presents them as organized, high-value entries:
`MOLSYSMT | WARNING (selection.py:42): Selection string is ambiguous. Hint: Use 'atom_name:...'`

### 4.3 Telemetry & Health Reports
The system can produce a summary of the session or health statistics on demand:
```python
smonitor.report()
# Output:
# Functions called: 124
# Warnings issued: 2 (1 in molsysmt, 1 in argdigest)
# Errors encountered: 0
# Peak memory: 450MB
```

### 4.5 Optional Profiling
When enabled (`profiling=True`), each context frame includes a `duration_ms` field
with the function execution time. This is lightweight and intended for QA/dev profiling,
not full performance analysis.

### 4.4 Symmetry with the "Digest" family
`monitor` will automatically find a `_smonitor.py` file in the project root to load library-specific diagnostic rules, hints, and formatting preferences.

---

## 5. Integration Strategy

To implement `monitor` across the UIBCDF suite:

1.  **Phase 1: Base Library**: Build the core manager, the `@signal` decorator, and the context tracker.
2.  **Phase 2: Emitter Injection**: Replace standard `logging` and `warnings` calls in `argdigest`, `depdigest`, etc., with `monitor.emit()`.
3.  **Phase 3: MolSysMT Adoption**: Use `monitor` as the primary engine for `msm.config.setup_logging()`.
4.  **Phase 4: Automated Documentation**: Integrate with Sphinx to show which functions are monitored and what signals they emit.

---

## 6. Future Ideas

- **Live Dashboard**: A tiny web or terminal dashboard showing real-time execution signals and library health.
- **AI-Agent Instructions**: Export signals as machine-readable instructions for LLM agents to better debug the library state.
- **Performance Profiling**: Combine diagnostics with time-tracking to identify bottlenecks in the call-stack without heavy external profilers.
- **CLI & Env Controls**: Provide a lightweight CLI and environment variables to toggle profiles and validate configuration.

---

> **Tagline:** `smonitor` — The precision telemetry system for the scientific Python stack.

---

# v0.2 (Draft) — Expanded Design Skeleton

**Status:** DRAFT  
**Notes:** This section extends v0.1 without breaking the original vision. It formalizes configuration discovery via `_smonitor.py`, profiles, and a policy engine, and introduces a communication style guide for user-facing messages.

## 1. Configuration Sources and Priority

Configuration can be provided by multiple sources. Higher priority overrides lower priority:

1. **Runtime call**: `smonitor.configure(...)`
2. **CLI arguments** (if a CLI exists): `--profile dev`, `--level INFO`, etc.
3. **Environment variables**: e.g., `SMONITOR_PROFILE=dev`
4. **Project file**: `_smonitor.py` at project root
5. **Internal defaults**

The active profile may be changed at runtime, and must override `_smonitor.py`.

## 2. `_smonitor.py` Schema (Project Root)

Every library in the ecosystem can define `_smonitor.py` in its root. This file declares preferences and rules; `smonitor` decides the final output.

```python
# _smonitor.py

PROFILE = "user"  # Default profile for this project

SMONITOR = {
    "level": "WARNING",
    "trace_depth": 3,
    "show_traceback": False,
    "capture_warnings": True,
    "capture_logging": True,
    "handlers": ["console"],
}

PROFILES = {
    "user": {
        "level": "WARNING",
        "show_traceback": False,
        "style": "user",
    },
    "dev": {
        "level": "INFO",
        "show_traceback": True,
        "style": "dev",
    },
    "qa": {
        "level": "INFO",
        "show_traceback": True,
        "style": "qa",
    },
    "agent": {
        "level": "WARNING",
        "show_traceback": False,
        "style": "agent",
    },
    "debug": {
        "level": "DEBUG",
        "show_traceback": True,
        "style": "debug",
    },
}

# Environment variables
# SMONITOR_PROFILE, SMONITOR_LEVEL, SMONITOR_TRACE_DEPTH,
# SMONITOR_CAPTURE_WARNINGS, SMONITOR_CAPTURE_LOGGING,
# SMONITOR_CAPTURE_EXCEPTIONS, SMONITOR_SHOW_TRACEBACK,
# SMONITOR_ARGS_SUMMARY, SMONITOR_PROFILING

# Policy Engine rules (routing + filtering)
ROUTES = [
    {"when": {"level": "WARNING", "source_prefix": "molsysmt.select"},
     "send_to": ["console", "json"]},
]

FILTERS = [
    {"when": {"code": "MSM-W010"}, "rate_limit": "1/100"},
]

# Message metadata (user/dev/qa/agent hints)
CODES = {
    "MSM-W010": {
        "title": "Selection ambiguous",
        "user_message": "La selección es ambigua.",
        "user_hint": "Especifica la selección con más detalle.",
        "dev_hint": "Usa selectors explícitos.",
    },
}

# Optional: signal contracts for docs/tests
SIGNALS = {
    "molsysmt.select": {
        "warnings": ["MSM-W010"],
        "errors": ["MSM-E120"],
        "extra_required": ["selection"],
    }
}
```

## 3. Policy Engine

The policy engine applies declarative rules to events **after** normalization and **before** handler dispatch. It can:

- route events to handlers,
- filter or rate-limit repetitive events,
- transform or enrich event fields.

### 3.1 Rule Format: `when`

`when` supports exact matches and operators. Supported keys:

- `level`, `source`, `source_prefix`, `category`, `code`, `tags`, `exception_type`, `library`

Operators:

- `eq` (default), `in`, `prefix`, `contains`, `regex`

Examples:

```python
{"when": {"level": "WARNING", "source_prefix": "molsysmt.form"}}
{"when": {"code": {"in": ["MSM-W010", "MSM-W011"]}}}
{"when": {"category": {"regex": ".*Dep.*"}}}
{"when": {"tags": {"contains": "io"}}}
```

## 4. Communication Style Guide (By Profile)

### 4.1 Global rules
- Always explain **what happened** and **how to fix it**.
- No blame; messages should feel helpful and collaborative.
- Links are optional; never required to understand the message.

### 4.2 Profile: `user`
Tone: clear, friendly, minimal jargon.

```
Error: <qué pasó>.
Solución: <qué hacer>.
Ejemplo: <ejemplo correcto>.
Más ayuda: <URL opcional>.
```

### 4.3 Profile: `dev`
Tone: precise, technical, contextual.

```
Error [CODE]: <mensaje>
Context: function=..., arg=..., value=...
Hint: ...
```

### 4.4 Profile: `qa`
Tone: systematic, reproducible.

```
[CODE] <mensaje> | function=... | input=...
Expected: yes/no
```

### 4.5 Profile: `agent`
Tone: structured, parsable.

```
code=... category=... action=... extra.foo=...
```

### 4.6 Profile: `debug`
Tone: deep diagnostics.

```
Error [CODE] (event_id=...):
Context chain: ...
Traceback (last N frames): ...
```

## 5. User-Facing Clarity Requirement

All exceptions and warnings intended for end users must:

1. Describe the problem in plain language.
2. Suggest a concrete fix or next step.
3. Avoid internal jargon unless the profile is `dev`/`debug`.
