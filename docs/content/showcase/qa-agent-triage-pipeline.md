# QA + Agent Triage Pipeline

This showcase targets maintainers of the host library running QA and AI-assisted triage.

## Problem

You need fast, reproducible diagnosis across many failures while keeping
human review as the final decision point.

## Pattern

Run strict diagnostics in CI, export structured bundles, and triage by stable
keys (`code`, `signal`, `trace_hash`).

```python
import smonitor

smonitor.configure(
    profile="qa",
    strict_signals=True,
    strict_schema=True,
    buffer_events=True,
)
```

```bash
pytest
smonitor export --out smonitor_bundle --max-events 500
```

Automation pipeline:
1. CI stores the bundle as an artifact.
2. Agent parses event stream in `agent` profile.
3. Triage groups incidents by `code` + `trace_hash`.
4. Agent proposes diagnosis and patch draft.
5. Maintainer reviews and merges only after tests pass.

## Why this works

- failures become comparable across runs and environments;
- triage focuses on stable contracts, not brittle free text;
- human ownership is preserved.

## Where to apply

- nightly test pipelines;
- release-candidate validation;
- large issue backlogs with repeated incident classes.
