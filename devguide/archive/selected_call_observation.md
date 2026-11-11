---
summary: Observe selected Python calls without replacing their callable or code identities.
issue: uibcdf/smonitor#65
status: resolved
opened: 2026-11-10
closed: 2026-11-10
verification: measured
area: [profiling, interoperability]
guard: tests/test_call_observation.py
normative: docs/content/developer/observation.md
blocked_by: []
supersedes: []
---

# Selected call observation

OpenCASTp requires its original functions, profile/trace hooks and GC callback
policy during diagnostic observations. The owner issue retains callable/code
aliasing, concurrent native-route selection and callback-policy evidence.

Assess `sys.monitoring` on CPython 3.12–3.14 with an explicitly owned tool slot,
bounded selected-code accounting, per-thread stacks and wall/thread-CPU clocks.
Record code aggregation versus callable identity, interrupted/unmatched events,
thread scope, unavailable native-receiver identity and unavailable GC timing.
Process CPU is a separate scope observation. Preserve all existing signal/span
interfaces and refuse unsupported backends or ownership conflicts explicitly.

## Implemented outcome

Executed current/all-thread, recursion, code/callable alias, bound/native receiver, return/unwind, tool conflict/cleanup and callback-clock error controls pass on CPython 3.14. Exact replay independently checks inclusive/exclusive wall and thread-CPU clocks.

The linked maintained contract states the supported input/backend and coverage
boundaries. Consumer receiving is coordinated under uibcdf/molsyssuite#181;
publication remains separately tracked in uibcdf/smonitor#67.
