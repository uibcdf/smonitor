Configuration
=============

Project configuration can be provided via `_smonitor.py` at the package root.
Runtime `smonitor.configure(...)` always overrides project defaults.

If you need to load a package-level `_smonitor.py`, pass `config_path`:

::

  smonitor.configure(config_path=Path(__file__).parent)

For libraries that want automatic configuration at import time, use
`smonitor.integrations.ensure_configured(package_root)`.

Schema
------

- `PROFILE`: default profile name
- `SMONITOR`: base config (level, trace_depth, capture_warnings, etc.)
- `PROFILES`: per-profile overrides
- `ROUTES`, `FILTERS`: policy engine rules
- `CODES`, `SIGNALS`: metadata for docs/tests and message templates

Common options in `SMONITOR`:

- `event_buffer_size`: number of recent events kept in memory for bundle export
- `strict_config`: if True, invalid `_smonitor.py` raises at configure time

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
- `SMONITOR_PROFILING_BUFFER`
- `SMONITOR_PROFILING_SAMPLE`
- `SMONITOR_EVENT_BUFFER`
- `SMONITOR_STRICT_SIGNALS`
- `SMONITOR_STRICT_SCHEMA`
- `SMONITOR_STRICT_CONFIG`
- `SMONITOR_ENABLED`

Logging Capture
---------------

By default, smonitor avoids installing a logging handler if the root logger
already has handlers. This minimizes interference with user-configured logging.

CLI
---

The CLI can validate `_smonitor.py` and print reports:

::

  smonitor --validate-config
  smonitor --check
  smonitor --check --check-level WARNING --check-code MSM-W010 --check-source molsysmt.select
  smonitor --check --check-event '{"level":"WARNING","message":"x","source":"molsysmt.select","code":"MSM-W010"}'
  smonitor --profile dev --report
  smonitor export --out smonitor_bundle --max-events 500
  smonitor export --out smonitor_bundle --drop-extra --redact extra.password

Config Validation
-----------------

`smonitor --validate-config` checks `_smonitor.py` for unknown keys and basic
type errors (SMONITOR/PROFILES/ROUTES/FILTERS/CODES/SIGNALS).

If `strict_config=True` (or `SMONITOR_STRICT_CONFIG=1`), invalid config raises
an exception at `smonitor.configure(...)`.

CLI returns non-zero exit codes:

- `0` on success
- `1` if no `_smonitor.py` is found (validate)
- `2` if config is invalid

Strict signals (dev/qa)
-----------------------

::

  smonitor.configure(profile="dev", strict_signals=True)

  # Missing required extras in SIGNALS will raise ValueError
