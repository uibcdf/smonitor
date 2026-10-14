# Using Bundles for Support

SMonitor supports local diagnostic bundles for reproducible troubleshooting.

## Why bundles help

- they capture structured diagnostics,
- they reduce guesswork in support,
- they speed up issue triage.

## Example export

```bash
smonitor export --out smonitor_bundle --max-events 500
```

## Privacy options

Use redaction and field dropping when needed:

```bash
smonitor export --out smonitor_bundle --drop-extra --redact extra.password
```

Only share bundles if you are comfortable with the included information.
