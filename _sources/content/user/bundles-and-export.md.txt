# Bundles and Export

Local bundles are privacy-first exports that capture current SMonitor state and recent events.

## Export examples

```bash
smonitor export --out smonitor_bundle --max-events 500
smonitor export --out smonitor_bundle --since 2026-02-06T00:00:00
smonitor export --out smonitor_bundle --drop-extra --redact extra.password
smonitor compare current_bundle.json previous_bundle.json --format markdown
```

Generated artifacts:
- `bundle.json` (config, policy, codes/signals, report)
- `events.jsonl` (optional recent events)

Use `--out bundle.json` for a single-file export.

Bundle comparisons focus on triage changes between runs:
- new/disappeared/recurrent incident fingerprints,
- code-count deltas,
- slow-signal deltas.

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

Lowering `event_buffer_size` immediately discards the oldest retained events.
Setting it to `0` clears the buffer and stops retention; raising it later starts
with an empty buffer. Bundle exports contain only events still retained at
collection time.

## Narrow identity bundle for strict consumers

`collect_identity_bundle()` and `export_identity_bundle()` are opt-in,
nonemitting alternatives when a consumer only needs bounded event identities:

```python
bundle = smonitor.collect_identity_bundle(
    max_events=20, allowed_codes={"MYLIB-W001"}
)
smonitor.export_identity_bundle(
    "support-identities.json", max_events=20, allowed_codes={"MYLIB-W001"}
)
```

This single-file JSON profile exports a schema, timestamp, fixed producer name,
coverage counts, a list of omitted sections, and at most 100 retained events.
Each event contains only a validated level, a 16-character fingerprint, and a
code if the application explicitly approved that exact code in `allowed_codes`.
The allowlist accepts up to 128 uppercase code identifiers; its strings remain
the application's responsibility. The profile excludes `argv`, paths, runtime
identifiers, configuration, catalogs, messages, source, context, extra, report,
and project configuration. It never flushes pending coalesced or duplicate
summaries or invokes handlers. It does not claim complete history: the buffer,
earlier filtering and pending summaries can omit observations. Fingerprints
support correlation and should not be treated as a secrecy guarantee.

The default `collect_bundle()` and `export_bundle()` remain the rich support
artifacts and keep their existing export behavior and redaction options.

## You are done when

- `smonitor export` generates the expected files,
- `smonitor compare` shows meaningful diffs across representative runs,
- sensitive fields are removed/redacted according to policy,
- your support workflow can reproduce issues from the exported bundle.
