---
summary: Execute the quick-start decorator with its supported public signature.
issue: uibcdf/smonitor#64
status: resolved
opened: 2026-11-10
closed: 2026-11-10
severity: medium
verification: reproduced
area: [documentation, signals]
guard: tests/test_documented_signal_examples.py
normative: docs/content/developer/profiling.md
blocked_by: []
supersedes: []
---

# Documented signal examples

The README and two documentation pages used `signal(name=...)`, which raises
`TypeError` at function definition on Python 3.14 with the current public
decorator. Signal identities derive from the callable's module and name.

All three examples now use `@smonitor.signal`. The guard extracts and executes
their actual Python blocks, then calls the documented function through normal
and diagnostic paths. It catches unsupported decorator keywords in published
examples and verifies that their diagnostic code reaches the public report.
