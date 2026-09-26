---
summary: CatalogWarning duplicates a hint when a wrapper supplies its catalog on rebuild.
issue: uibcdf/smonitor#21
status: resolved
opened: 2026-09-22
closed: 2026-09-26
severity: high
verification: inspected
area: [catalog, integrations, warnings]
guard: tests/test_catalog_instance_round_trip.py::test_catalog_bound_wrapper_preserves_the_visible_text_on_rebuild
normative:
blocked_by: []
supersedes: []
---

# CatalogWarning duplicates a hint when a wrapper supplies its catalog on rebuild

**Reported:** 2026-09-22 by MolSysMT after its warning reconstruction tests
found duplicated hints with SMonitor 0.16.0.

## What

`type(warning)(*warning.args)` appended the catalog hint a second time when
the consumer subclass always passed `catalog` and `meta` to `super().__init__()`.
The instance's `args` already held the complete visible text.

## How

`CatalogWarning.__init__` treated an explicit message as an args-only rebuild
only if `catalog`, `meta` and `extra` were all absent. The wrapper supplied the
first two on every call, but they do not recover the fields of the occurrence.
The constructor now treats an explicit message with no occurrence-specific
`extra` as authoritative, even when catalog and library metadata are present.

## Why

MolSysMT's warning round-trip tests exposed the duplicate user-facing hint.
An args-only transport must preserve the visible text without pretending that
lost structured fields can be reconstructed.

## What was refuted

Re-resolving the hint from the catalog does not solve the transport problem:
the hint may interpolate fields absent from `args`. Supplying a catalog or
library metadata on rebuild is not proof that those fields survived.

## Resolution

Commit `90a4d59` preserves the text in the consumer-wrapper shape. The guard
constructs a warning with a field-dependent hint, rebuilds it from `args`, and
asserts that the text and `args` remain exact and the hint appears once. Local
pytest passed 518 tests with three skips; the hosted CI, QA and documentation
checks for the commit passed. MolSysMT's own suite was not rerun for this record.
