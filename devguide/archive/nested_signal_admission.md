---
summary: Preserve outer exception observations after filtered inner signals.
issue: uibcdf/smonitor#59
status: resolved
opened: 2026-11-04
closed: 2026-11-04
verification: measured
area: [maintenance, contracts]
guard: tests/test_nested_signal_filtering.py
normative:
blocked_by: []
supersedes: []
severity: high
---

# Nested signal admission

The consumer reproduction in uibcdf/dockingmt#19 was reproduced before repair:
12 of 24 new controls failed. A constructed event returned by Manager.emit did
not imply threshold admission, yet the wrapper marked the exception emitted.

An internal context-local receipt now records admission after enabled/silence/
threshold decisions, before aggregation/routing. Public emit return dictionaries
and payloads are unchanged. Only an admitted observation sets the existing
exception marker. Accepted inner DEBUG remains the single observation; it is
not escalated by an outer ERROR. Filtered or silenced inner DEBUG permits the
outer ERROR. Handler success and complete history are not claimed by admission.

The 24 sync/async, detailed/restrictive, disabled, threshold and silence controls
pass after repair. One hundred related core/capture/signal tests also passed.
They verify actual handler/buffer observations and original exception identity,
args and cause; the guard protects the reported mechanism rather than marker
shape alone. Source publication is distinct from future public-file receiving.
ArgDigest composition makes the shared-provider notice applicable; coordinate
receiving with uibcdf/molsyssuite#106 and uibcdf/dockingmt#19.

## Receiving controls, 2026-11-04

Three additional controls change threshold, enabled state or source silence
during exception formatting. All 27 owning controls pass: admission follows
the final manager policy rather than an earlier decorator eligibility guess.
The independently opened receiving records are uibcdf/molsyssuite#163 and
uibcdf/argdigest#49; those owners retain consumer and public receiving.

## Concurrent owner contribution, 2026-11-04

Liliana's independently prepared PR uibcdf/smonitor#60 at
f0ef19a368b8ad0295e9f22a02435ac56426c772 adds nineteen useful controls and
protects the receipt against reentrant diagnostic callbacks. Against main
7fad8f5, eighteen controls pass and its nested-callback control fails: an
unrelated admitted callback could acknowledge the filtered exception.

The integration preserves her tests and user edge-case guidance with authorship
credit. A receipt is now claimed by its exact manager call, and native exception
formatting runs before receipt tracking. A twentieth control covers a formatter
that emits a separate diagnostic. All 47 combined owning controls pass. Direct
main integration follows Diego's standing authorization; PR closure records the
adopted commit rather than claiming that the parallel branch was merged.
