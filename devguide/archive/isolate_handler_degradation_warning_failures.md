---
summary: Keep handler-degradation warning failures from escaping direct emission
issue: uibcdf/smonitor#42
status: resolved
opened: 2026-10-13
closed: 2026-10-13
severity: medium
verification: reproduced
area: [manager, handlers, warnings]
guard: tests/test_hardening.py::test_handler_warning_as_error_does_not_escape_direct_emit
normative: docs/content/user/library-integrators/handlers-and-routing.md
blocked_by: []
supersedes: []
---

# Keep handler-degradation warning failures from escaping direct emission

## What and why

With a failing handler and `handler_error_threshold=1`, a Python warning
filter promoting `RuntimeWarning` to an error made direct `emit()` raise while
announcing handler degradation. The caller could lose its native return path,
later handlers were skipped, and the event was not retained in the manager
buffer. The handler fault itself remains an ordinary isolated sink failure.

## Resolution

The degradation announcement now uses the stable internal catalog template
`SMONITOR-HANDLER-DEGRADED`. The manager records the error count and warning
before attempting the Python warning, and isolates ordinary warning-delivery
exceptions while retaining the event and attempting later handlers. The
warning still reaches callers under ordinary warning filters. The guard
failed against the previous source and now checks direct emission with
warnings-as-errors, both handlers, retained events and the bounded warning
record on Python 3.14.

## Scope

The isolated path catches ordinary exceptions from the announcement; it does
not catch `BaseException` subclasses. Other direct-emission validation errors
retain their own contracts.
