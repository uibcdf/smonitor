---
summary: Enforce a lowered event-buffer capacity on retained history
issue: uibcdf/smonitor#41
status: resolved
opened: 2026-10-13
closed: 2026-10-13
severity: medium
verification: reproduced
area: [manager, bundle, configuration]
guard: tests/test_bundle.py::test_event_buffer_resize_trims_history_and_bundle_immediately
normative: docs/content/user/bundles-and-export.md
blocked_by: []
supersedes: []
---

# Enforce a lowered event-buffer capacity on retained history

## What and why

The event insertion path previously removed only one item when over capacity.
After shrinking an existing four-event buffer to two, later insertions could
leave four events retained and exported. This broke the configured count bound
used by support bundles, though it was never a byte or privacy guarantee.

## Resolution

`Manager.configure(event_buffer_size=...)` now trims existing history
immediately to the newest events. A nonpositive value clears history and stops
retention; raising the limit later starts with an empty buffer. Insertion uses
the same private resize operation, so an oversized backlog cannot persist.
The public bundle guide documents these semantics. The guard failed against
the previous source and now checks shrinking, insertion, bundle collection,
disabling and re-enabling retention on Python 3.14.

## Scope

This is a count-capacity contract. It does not claim aggregate byte limits or
remove already exported artifacts.

## Publication (2026-10-14)

The fix is available in the stable [0.21.0 release](https://github.com/uibcdf/smonitor/releases/tag/0.21.0)
and the exact Conda `py_2` artifact, qualified by the
[installed matrix](https://github.com/uibcdf/smonitor/actions/runs/38525100772).
