# SMonitor End-User Guide for Libraries

This document is a canonical template for maintainers of library `A` that embeds
SMonitor and needs a clear end-user section in `A` documentation.

## Purpose

Help users of `A` interpret diagnostics as guidance, not noise.

## Minimal section to include in library A docs

1. What these messages are:
- warnings/errors produced by `A` with SMonitor support.
- messages are designed to help users complete tasks with fewer retries.
2. How to interpret levels:
- `WARNING`: operation usually continues, but quality/ambiguity should be reviewed.
- `ERROR`: operation failed; apply fix hint and retry.
3. 30-second rescue flow:
- read message and hint,
- apply fix and retry once,
- if failure persists, report with code/message and reproducer.
4. Support payload:
- exact message + code ID,
- minimal reproducer,
- environment and version,
- optional redacted bundle.
5. Link to extended online docs:
- https://uibcdf.github.io/smonitor/content/user/end-users/index.html

## Required A-specific customization

Each library `A` should add:
- common code IDs used in `A`,
- how users change verbosity/profile in `A` (if exposed),
- where users report issues for `A`.

## Canonical companion

Use `SMONITOR_END_USER_RESCUE_CARD.md` as a one-screen quick rescue block.
