---
summary: The signal wrapper shifts Python warning attribution into SMonitor.
issue: uibcdf/smonitor#23
status: resolved
opened: 2026-09-24
closed: 2026-09-26
verification: inspected
area: [integrations, warnings, documentation]
guard: tests/test_catalog_warning_python_semantics.py::test_catalog_warning_inside_signal_blames_its_application_caller
normative: standards/SMONITOR_GUIDE.md
blocked_by: []
supersedes: []
---

# The signal wrapper shifts Python warning attribution into SMonitor

**Reported:** 2026-09-24 by Sabueso while attributing warnings from
functions decorated with `@signal`.

## What

`DiagnosticBundle.warn()` counted `@signal`'s wrapper frame in `stacklevel`.
With the ordinary default, warning records pointed into
`smonitor/core/decorator.py` instead of at the application caller.

## How

The bundle now counts application frames and skips SMonitor frames when it
calculates the `warnings.warn` stacklevel. `warn_once` uses the same calculation
without manually adding a frame. The canonical guide documents the limit:
plain `warnings.warn()` inside a decorated function still counts the wrapper.

## Why

Warning filters, pytest warning records and user tracebacks need an accurate
filename and line number. Consumer packages should not need a constant tied
to SMonitor's internal wrapper depth.

## What was refuted

Changing `@signal` cannot alter the stacklevel of an arbitrary plain
`warnings.warn()` call inside the decorated function. That case needs an
adjusted application stacklevel or catalog emission through the bundle.

## Resolution

Commit `90a4d59` adds a guard for both `warn` and `warn_once` inside `@signal`;
it checks the exact filename and caller line. Local pytest passed 518 tests
with three skips, and the hosted checks for the commit passed.
