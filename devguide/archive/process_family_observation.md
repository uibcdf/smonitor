---
summary: Sample an explicitly owned Linux process family with bounded resource and coverage evidence.
issue: uibcdf/smonitor#66
status: resolved
opened: 2026-11-10
closed: 2026-11-10
verification: measured
area: [profiling, resources]
guard: tests/test_process_observation.py
normative: docs/content/developer/observation.md
blocked_by: []
supersedes: []
---

# Process-family resource observation

OpenCASTp retains observed PSS read gaps, observer overhead and an all-TID child
discovery correction in the owner issue. The intended observer is a sibling of
the measured calculation and operates in a caller-selected finite window.

Design bounded PID/start-tick discovery across all task children, raw timestamped
read errors, sample/read spans, requested wait, observer CPU and explicit
incomplete coverage. Distinguish sampled PSS/RSS, root self/joined-child CPU,
observed descendants, pressure/capacity and application-owned execution policy.
Missing process/read evidence must remain unavailable. Linux `/proc` is the
initial supported boundary; other platforms require an explicit refusal.

## Implemented outcome

An actual sibling observer discovers a child created by a secondary thread and preserves parent-owned exit 17. Error, PID reuse, reparenting, identity-read races, metadata limits, finite windows and exception cleanup controls pass. Missing operation values remain unavailable.

The linked maintained contract states the supported input/backend and coverage
boundaries. Consumer receiving is coordinated under uibcdf/molsyssuite#181;
publication remains separately tracked in uibcdf/smonitor#67.
