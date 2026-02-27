# Bundles and Export

Local bundles are privacy-first exports that capture current SMonitor state and recent events.

## Export examples

```bash
smonitor export --out smonitor_bundle --max-events 500
smonitor export --out smonitor_bundle --since 2026-02-06T00:00:00
smonitor export --out smonitor_bundle --drop-extra --redact extra.password
```

Generated artifacts:
- `bundle.json` (config, policy, codes/signals, report)
- `events.jsonl` (optional recent events)

Use `--out bundle.json` for a single-file export.

## Privacy controls

- `--drop-extra`
- `--drop-context`
- `--redact`

## Redaction policy examples

Minimal redaction (keep context, hide credentials):

```bash
smonitor export --out smonitor_bundle --redact extra.password --redact extra.token
```

Support-share export (hide local paths and usernames):

```bash
smonitor export \
  --out smonitor_bundle \
  --redact context.cwd \
  --redact context.user \
  --redact extra.local_path
```

Strict export for external sharing:

```bash
smonitor export --out smonitor_bundle --drop-extra --drop-context
```

## Buffer requirement

Event exports require buffering:

```python
SMONITOR = {"event_buffer_size": 500}
```

## You are done when

- `smonitor export` generates the expected files,
- sensitive fields are removed/redacted according to policy,
- your support workflow can reproduce issues from the exported bundle.
