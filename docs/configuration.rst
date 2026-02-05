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
- `CODES`, `SIGNALS`: metadata for docs/tests and message templates

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
- `SMONITOR_PROFILING`
- `SMONITOR_STRICT_SIGNALS`
- `SMONITOR_STRICT_SCHEMA`
- `SMONITOR_ENABLED`

CLI
---

The CLI can validate `_smonitor.py` and print reports:

::

  smonitor --validate-config
  smonitor --check
  smonitor --check --check-level WARNING --check-code MSM-W010 --check-source molsysmt.select
  smonitor --check --check-event '{"level":"WARNING","message":"x","source":"molsysmt.select","code":"MSM-W010"}'
  smonitor --profile dev --report

Config Validation
-----------------

`smonitor --validate-config` checks `_smonitor.py` for unknown keys and basic
type errors (SMONITOR/PROFILES/ROUTES/FILTERS/CODES/SIGNALS).

Strict signals (dev/qa)
-----------------------

::

  smonitor.configure(profile="dev", strict_signals=True)

  # Missing required extras in SIGNALS will raise ValueError
