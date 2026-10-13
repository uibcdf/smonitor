---
summary: Preserve exception emission when argument repr fails
issue: uibcdf/smonitor#36
status: resolved
opened: 2026-10-13
closed: 2026-10-13
severity: medium
verification: reproduced
area: [signal, capture, integration]
guard: tests/test_signal_exception_code.py::test_argument_repr_failure_preserves_exception_event
normative:
blocked_by: []
supersedes: []
---

# Preserve exception emission when argument repr fails

## What and why

Ackredit reported that a lazy module argument whose `repr()` raises could
prevent the `@signal` exception event from being emitted. The producer's
original exception still propagated, but its catalog identity disappeared
from SMonitor telemetry. This affects diagnostic coverage on error paths;
Ackredit owns its consumer adoption.

## Diagnosis and resolution

The original issue identified the argument-summary call inside the exception
emission try block. Commit `6feac972` (2026-10-06) had already moved
`set_frame_args(..., _summarize_args(...))` into a separate guarded block in
`smonitor/core/decorator.py`. The current Python 3.14 source therefore emits
the catalog exception even when argument representation fails. The new guard
uses a lazy `ModuleType` whose `__getattr__` raises during `repr`, asserts the
original `CatalogException` and its exact event code, and observes the
catalog-driven fallback warning. This closes the missing verification rather
than changing the existing signal implementation.

## Scope

The guard proves current source behavior; the earlier Ackredit report was
source evidence. It does not qualify any future installed consumer artifact.
