# Audit CLI

The SMonitor CLI helps you validate configuration and generate reproducible diagnostics artifacts.

## Core commands

Validate project config:

```bash
smonitor --validate-config --config-path /path/to/package
```

Run a check event quickly:

```bash
smonitor --check --check-level WARNING --check-source mylib.api
```

Run a structured check event:

```bash
smonitor --check --check-event '{"level":"WARNING","message":"x","source":"mylib.api","code":"MYLIB-W001"}'
```

Export local bundle:

```bash
smonitor export --out smonitor_bundle --max-events 500
```

## When to use CLI in your workflow

Use CLI checks in:
- pre-commit validation of docs/config changes,
- CI smoke tests,
- release gate verification,
- support triage sessions.

## Suggested CI smoke block

```bash
pytest -q
smonitor --check --config-path .
smonitor export --out /tmp/smonitor_bundle --no-events --force
```

## Notes

- `--check` is useful for fast sanity checks.
- `export` is local-first; users decide if they share bundles.
- for sensitive environments, use redact options during export.
