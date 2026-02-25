# SMonitor End-User Guide for Libraries

This document is a canonical template for maintainers of a host library that embeds
SMonitor and needs a clear end-user section in the host library documentation.

## Purpose

Help users of the host library interpret diagnostics as guidance, not noise.

## Minimal section to include in host library docs

1. What these messages are:
- warnings/errors produced by the host library with SMonitor support.
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

## Required Host-Library Customization

Each host library should add:
- common code IDs used in the host library,
- how users change verbosity/profile in the host library (if exposed),
- where users report issues for the host library.

## Canonical companion

Use `SMONITOR_END_USER_RESCUE_CARD.md` as a one-screen quick rescue block.
