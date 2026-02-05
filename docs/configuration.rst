Configuration
=============

Project configuration can be provided via `_smonitor.py` at the project root.
Runtime `smonitor.configure(...)` always overrides project defaults.

Schema
------

- `PROFILE`: default profile name
- `SMONITOR`: base config (level, trace_depth, capture_warnings, etc.)
- `PROFILES`: per-profile overrides
- `ROUTES`, `FILTERS`: policy engine rules
- `CODES`, `SIGNALS`: metadata for docs/tests

Priority
--------

1. `smonitor.configure(...)`
2. CLI (if available)
3. Environment variables
4. `_smonitor.py`
5. Internal defaults

Environment Variables
---------------------

- `SMONITOR_PROFILE`
- `SMONITOR_LEVEL`
- `SMONITOR_TRACE_DEPTH`
- `SMONITOR_CAPTURE_WARNINGS`
- `SMONITOR_CAPTURE_LOGGING`
- `SMONITOR_CAPTURE_EXCEPTIONS`
- `SMONITOR_SHOW_TRACEBACK`
- `SMONITOR_ARGS_SUMMARY`

CLI
---

The CLI can validate `_smonitor.py` and print reports:

::

  smonitor --validate-config
  smonitor --profile dev --report
