# Collective Evidence Pack

This document is the cross-repo handoff artifact for collective validation with:
- `../depdigest`
- `../argdigest`
- `../pyunitwizard`

## What this is

`collective_evidence_pack.md` is the canonical checkpoint record for SMonitor:
- local evidence already validated in this repository,
- required cross-library E2E evidence,
- pending items that cannot be closed locally.

## How to use this file

1. Before each RC/stabilization checkpoint:
- refresh local evidence and references.

2. During cross-repo synchronization:
- compare status notes across all four repositories.

3. At go/no-go decisions:
- use decision placeholders to record owner, date, blockers, and evidence links.

## How to update this file

1. Update metadata (`Date`, `baseline`, `head reference`).
2. Refresh local quality and compatibility evidence.
3. Keep only reproducible, in-repo references.
4. Do not mark collective closure from local-only evidence.

Date: `2026-03-03`
SMonitor baseline: `0.11.4` (pre-1.0 stabilization)
SMonitor head reference for this pack: `cabb2d0`

## 1. Local quality baseline (SMonitor)

- Source status and quality snapshot references:
  - `devguide/README.md`
  - `devguide/implementation_plan.md`

## 2. Contract evidence index (SMonitor)

Use this section to keep concrete, local references for:
- shared collective error-path E2E module: `tests/e2e/test_collective_error_path.py`,
- event schema stability,
- profile behavior (`user`, `dev`, `qa`, `agent`),
- traceability tags and category semantics,
- bundle export contract and reproducibility path,
- integration behavior with sibling libraries.

## 3. Collective E2E target scenario (must be validated across repos)

Goal:
- an error raised in PyUnitWizard unit/conversion paths is surfaced as:
  1. ArgDigest contract error with caller context,
  2. SMonitor event/log with stable code and profile-consistent output,
  3. DepDigest remediation hint when dependency-related.

Minimum acceptance evidence:
- reproducible command/workflow,
- captured output/events or artifact,
- per-library references to tests/commits proving the path.

## 4. Shared status template

```md
Status note (YYYY-MM-DD):
- smonitor: <done locally|in progress|blocked|pending> (<reference>)
- depdigest: <done locally|in progress|blocked|pending> (<reference>)
- argdigest: <done locally|in progress|blocked|pending> (<reference>)
- pyunitwizard: <done locally|in progress|blocked|pending> (<reference>)
- collective validation: <pending|in progress|done> (<evidence>)
```

## 5. Status note (2026-03-03)

- smonitor: in progress (`devguide/implementation_plan.md` 1.0 stabilization section)
- depdigest: pending
- argdigest: in progress (consumer side profile parity pending collective evidence)
- pyunitwizard: done locally (`pyunitwizard/devguide/collective_evidence_pack.md`)
- collective validation: pending

## 6. Pending collective closures (from SMonitor perspective)

- finalize cross-library traceability label contract by failure class,
- lock collective evidence for profile parity across all sibling libraries,
- confirm host-level health validation path across all four layers.

## 7. Decision log placeholders

- `go/no-go owner`:
- `date`:
- `collective evidence links`:
- `open blockers`:
- `resolution plan`:
