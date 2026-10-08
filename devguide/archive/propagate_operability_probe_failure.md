---
summary: The operability evidence CLI hides failed test and comparison outcomes.
issue: uibcdf/smonitor#44
status: resolved
opened: 2026-10-08
closed: 2026-10-08
severity: medium
verification: reproduced
area: [devtools, resources]
guard: tests/test_operability_evidence.py
normative:
blocked_by: []
supersedes: []
---

# The operability evidence CLI hides failed test and comparison outcomes.

## What

At c7bfb0b69b4f26e140c5b1668db76c3174b3f2b7, a controlled failing pytest
suite prints pytest exit=1 and retains requested diagnostic JSON, but the
operability CLI returns zero. Optional comparison failure is discarded too.

## How

Four real CLI cases exercise passing/failing one-test suites with and without
a malformed-JSON comparison baseline, retaining reports and preserving caller
files. A fifth focused control fixes pytest exit=2 and comparison exit=7 to
verify suite failure remains primary. Four fail before; the pure-success control
passes. No component scientific suite is invoked by this guard.

## Why

Useful evidence after failure must not be interpreted as successful execution.
This is owner-local developer orchestration under uibcdf/molsyssuite#104, with
possible effects on operators invoking the source helper. Runtime APIs, package
artifacts, guide bytes and consumer dependency/pins remain unchanged.

## What was refuted

An initial comparison fixture used {}; the existing comparator accepts that
as an empty baseline. That expectation was invalid. It was replaced by malformed
JSON, and all eleven new custody/outcome guards were rerun against original
operations: seven fail, four controls pass. The corrected guard protects an
actual nonzero comparison outcome, not a new format-validation contract.
Removing failure evidence or changing the scientific test selection would
weaken support; both are deliberately preserved. No new subprocess framework,
retry, timeout, generator or serialized boundary is introduced.

## Resolution

The existing main operation returns suite status, or optional comparison status
when the suite succeeded. Comparison still runs to retain diagnostic value;
requested bundles and baseline/caller inputs are not deleted. Five guards pass;
local/full/native evidence is linked in the owning issue. This changes source
operator failure handling, not public runtime bundle semantics.

Qualified Python 3.14.7: all 653 ordinary source tests pass with two explicit
skips (one collective sibling case absent in isolated workspace, one reported
without resolved reason by the receptor). The unchanged central provider
25363f2a2c902c04b2cdc8b301a3e1c1ff0c0918 verifies fifteen declared-and-installed
public-bound routes. Both probe helps, whole-repository Ruff (126 formatted
files), local report/index checks and central offline governance guard pass.
No public package/installed matrix, solver or deferred scientific suite invoked.
Native exact-source gates and source-only operator notice delivery are retained
in the owning issue and central #104 receipt before board closeout.

### Skip clarification — 2026-10-08

The literal "not resolved" skip is intentional in
`test_a_resolved_report_names_a_guard_or_a_normative_document`: a non-resolved record does not require a
resolved guard. Source inspection identifies its reason; no receptor defect or
missing source-test evidence is inferred from that label. The other skip is the
explicitly absent collective sibling fixture.
