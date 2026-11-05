---
summary: Callback diagnostics must not acknowledge another filtered event
issue: uibcdf/smonitor#61
status: resolved
opened: 2026-11-04
closed: 2026-11-04
severity: medium
verification: measured
area: [signals, filtering, callbacks]
guard: tests/test_signal_filtering.py
normative:
blocked_by: []
supersedes: []
---

# Nested callback emission receipts

The ordinary #59 correction is already delivered in b1241ef. On current main
82dad5a7e26e0fba712e30657a6739188d770d79, twenty additional controls yield
eighteen passes/two failures: a diagnostic emitted by exception formatting or
template resolution can acknowledge the exception's filtered DEBUG event.
The outer ERROR is then suppressed even though its own event was never accepted.

The follow-up retains the delivered private admission helper and public API.
Message construction precedes its receipt scope; each manager invocation claims
one receipt at entry, so nested callback events cannot acknowledge the parent.
The original threshold, silence, disabled, first-accepted deduplication, capture
and dictionary-return contracts remain unchanged. No consumer workaround,
diagnostic code, dependency floor or scientific behavior is introduced.

All twenty guards pass after hardening; the two failing current-main controls
directly assert that the callback event and one enclosing ERROR both reach the
handler, with native exception identity preserved. Broader provider/consumer
and private package evidence belongs in #61/#60, MolSysSuite #163 and DockingMT
#19. The owner-review PR carries this closeout; the issue closes on acceptance
and merge. Source receiving does not qualify a public package.
