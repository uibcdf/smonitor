# QA + Agent Triage Pipeline

This showcase targets maintainers of the host library running QA and AI-assisted triage.

## Problem

You need fast, reproducible diagnosis across many failures while keeping
human review as the final decision point.

## Pattern

Run strict diagnostics in CI, export structured bundles, and triage by stable
keys (`code`, `signal`, `fingerprint`).

```python
import smonitor

smonitor.configure(
    profile="qa",
    strict_signals=True,
    strict_schema=True,
    event_buffer_size=500,
)
```

```bash
pytest
smonitor export --out smonitor_bundle --max-events 500
```

Automation pipeline:
1. CI stores the bundle as an artifact.
2. Agent inspects `triage`, `normalized`, and `human_summary`.
3. Triage groups incidents by `code` + `fingerprint`.
4. If needed, compare against a previous bundle.
5. Agent proposes diagnosis and patch draft.
6. Maintainer reviews and merges only after tests pass.

## Deterministic triage key

For repeated incidents across runs, use the stable `fingerprint` already emitted
by SMonitor rather than rebuilding your own grouping key downstream.

This avoids brittle grouping by free text while keeping incidents comparable.

## Why this works

- failures become comparable across runs and environments;
- triage focuses on stable contracts, not brittle free text;
- human ownership is preserved.

## Where to apply

- nightly test pipelines;
- release-candidate validation;
- large issue backlogs with repeated incident classes.
