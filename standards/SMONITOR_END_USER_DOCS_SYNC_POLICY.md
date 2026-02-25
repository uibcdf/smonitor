# Sync Policy: End-User Diagnostics Docs for Library A

This policy defines how library `A` keeps its local end-user diagnostics docs
aligned with SMonitor canonical content.

## Canonical sources (source of truth)

- `SMONITOR_END_USER_GUIDE_FOR_LIBRARIES.md`
- `SMONITOR_END_USER_RESCUE_CARD.md`
- `SMONITOR_END_USER_DOCS_TEMPLATE.md`

## Local copy requirements in A

Each local copy in `A` should include metadata header:

```text
Source: smonitor/standards/SMONITOR_END_USER_DOCS_TEMPLATE.md
Synced from: smonitor@<tag-or-commit>
Last sync date: YYYY-MM-DD
```

## Sync cadence

Minimum recommended:
- when `A` updates SMonitor dependency,
- before each `A` release,
- whenever canonical standards above change.

## Drift detection

Drift is present when:
- local copy in `A` lacks required rescue/interpreting sections,
- sync metadata is missing or outdated,
- local semantics contradict canonical guidance.

## Conflict rule

`A` can customize wording and examples, but must preserve:
- meaning of `WARNING` vs `ERROR`,
- rescue flow,
- support payload expectations,
- pointer to extended SMonitor end-user docs.
