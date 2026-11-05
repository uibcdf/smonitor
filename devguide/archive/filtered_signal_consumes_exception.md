---
summary: A filtered inner signal hides an eligible enclosing exception event
issue: uibcdf/smonitor#59
status: resolved
opened: 2026-11-04
closed: 2026-11-04
severity: medium
verification: measured
area: [signals, filtering, capture, interoperability]
guard: tests/test_signal_filtering.py
normative:
blocked_by: []
supersedes: []
---

# A filtered inner signal consumes an exception observation

## What

At application threshold WARNING, an inner signal using exception_level=DEBUG
marks the raised exception emitted even though Manager.emit filters its event.
An enclosing ERROR signal then omits the same exception. The native exception
still propagates; diagnostic observation is lost. DockingMT #19 reproduces this
with its preparation signal around ArgDigest's DEBUG wrapper.

The independent reproduction is in uibcdf/smonitor#59. Verified starting source
is a3fd6d9858973b887e7a8ef0ed1b44f1dd1f2a1d; the runtime files are unchanged from
the original ebdd0542156ed1dbe8df93141dbddbc74132a6f0 report. Nineteen regression
cases on an isolated starting-source export yield **13 failures / 6 passes**.

## How

The signal wrapper unconditionally sets __smonitor_emitted__ after Manager.emit
returns. That method deliberately returns a dictionary preview for a threshold-
filtered/disabled event, and an empty dictionary for a silenced source. Its
return value therefore does not prove acceptance. Source silence and disabling
diagnostics during a call reproduce the same unwanted marker.

The correction adds a private scoped receipt for the exact manager
emission. The manager acknowledges it only after enablement, source silence and
level filtering. A nested callback emission cannot acknowledge its parent's
event. The context-local receipt is reset after success or failure and is absent
from public event dictionaries, bundles and signatures. Public emit previews
remain unchanged, and signal still calls the public manager emission route.

Only accepted observations set the existing exception marker. The first accepted
observation continues to win: an accepted DEBUG event at threshold DEBUG still
suppresses a later enclosing ERROR event, and nested ERROR signals emit once.
Coalescing/duplicate-policy handling remains an accepted logical observation;
this does not promise delivery to a particular handler. Native exception identity,
args, cause, catalog code/fields and restricted capture retain their contracts.

## Why

The affected arrangement is a supported orchestration pattern, not a downstream
misuse to repair by clearing the marker or reordering decorators. Provider-owned
acceptance is needed because application policy can change during a call or even
while exception text is constructed. MolSysSuite #163 records the advance shared
impact notice; DockingMT #19 owns concrete receiving and ArgDigest supplies the
observed nested wrapper. Other registered consumers remain candidates rather
than verified affected workflows.

## What was refuted

- Truthiness of emit's return is not acceptance; a filtered preview is nonempty.
- Checking the threshold before constructing an event is insufficient. A
  controlled exception formatter changes the threshold before the actual emit.
- A callback's separate accepted diagnostic must not consume the exception's
  filtered observation; a distinct nested-emission guard verifies this.
- Promoting every accepted DEBUG to ERROR changes existing deduplication and is
  not part of this correction.
- Wrapping/replacing native failures, changing application policy or patching
  consumer decorators would hide the shared defect rather than fix its owner.

## Verification and disposition

The nineteen guards cover sync/async filtering, accepted DEBUG and ERROR,
case-insensitive levels, exact/prefix silence, disabled/dynamically changed
policy, metadata-only capture, native identity/cause, public preview returns,
format-time reconfiguration and nested diagnostic callbacks. They pass with the
correction. Exact-branch full-suite, docs/package smoke, consumer
receiving and PR/CI evidence are recorded in the linked owner/coordination issues.

The candidate resolves the defect with guard tests/test_signal_filtering.py.
The owner-review PR carries implementation, guard and this archive together;
the GitHub issue closes on acceptance/merge, not on local verification. No
release, public provider version or consumer floor is selected. Consumer/source
receiving and later public artifacts keep their independent evidence.

## Concurrent-delivery correction — 2026-11-04

This supplementary record describes the independently tested candidate
f0ef19a368b8ad0295e9f22a02435ac56426c772, not its acceptance into main. While
it was being prepared, b1241ef delivered the ordinary #59 correction; its
authoritative closeout is nested_signal_admission.md. Current main
82dad5a7e26e0fba712e30657a6739188d770d79 passes eighteen of the expanded twenty
guards. The two remaining callback-receipt cases are separately owned by #61.
The review branch now retains the delivered implementation and adds only that
hardening. Prior source/build identities above are not relabeled as main or
public artifacts; see nested_callback_receipt.md for the final follow-up.
