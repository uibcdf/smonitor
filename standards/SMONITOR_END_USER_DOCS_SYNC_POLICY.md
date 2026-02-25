# Sync Policy: End-User Diagnostics Docs for Host library

This policy defines how a host library keeps its local end-user diagnostics docs
aligned with SMonitor canonical content.

## Canonical sources (source of truth)

- `SMONITOR_END_USER_GUIDE_FOR_LIBRARIES.md`
- `SMONITOR_END_USER_RESCUE_CARD.md`
- `SMONITOR_END_USER_DOCS_TEMPLATE.md`

## Local Copy Requirements in the Host Library

Each local copy in the host library should include a metadata header:

```text
Source: smonitor/standards/SMONITOR_END_USER_DOCS_TEMPLATE.md
Synced from: smonitor@<tag-or-commit>
Last sync date: YYYY-MM-DD
```

## Sync cadence

Minimum recommended:
- when the host library updates the SMonitor dependency,
- before each host-library release,
- whenever canonical standards above change.

## Drift detection

Drift is present when:
- local copy in the host library lacks required rescue/interpreting sections,
- sync metadata is missing or outdated,
- local semantics contradict canonical guidance.

## Conflict rule

The host library can customize wording and examples, but must preserve:
- meaning of `WARNING` vs `ERROR`,
- rescue flow,
- support payload expectations,
- pointer to extended SMonitor end-user docs.
