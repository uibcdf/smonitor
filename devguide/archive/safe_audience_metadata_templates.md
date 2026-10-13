---
summary: Evaluate audience-specific safe hints for metadata-only resolution
issue: uibcdf/smonitor#39
status: resolved
opened: 2026-10-13
closed: 2026-10-13
verification: reproduced
area: [catalog, capture, integration]
guard: tests/test_metadata_audience_templates.py::test_safe_audience_templates_are_pure_and_use_approved_facts
normative: docs/content/user/library-integrators/scoped-capture.md
blocked_by: []
supersedes: []
---

# Safe audience metadata templates

## What and why

Recorda's inspection-presentation analysis (uibcdf/recorda#14) needed
different actionable hints for users restoring retained bytes and developers
checking an index binding, while retaining metadata-only capture. Existing
`metadata_hint` applied one shared hint; ordinary `user_hint` and `dev_hint`
were intentionally unavailable in the restrictive path. A shared hint was a
valid first consumer slice, so this provider capability was not a blocker.

## Resolution

SMonitor now accepts optional `metadata_messages` and `metadata_hints` maps in
catalog entries. Their only audience keys are `user`, `dev`, `qa`, and `agent`;
`debug` follows `dev`. Exact audience templates precede the existing shared
metadata fields. Missing audience entries retain shared and ordinary-message
fallbacks, but never import ordinary profile hints into restrictive capture.
Provider registration validates each declared template as a bounded string
with direct named fields only. Runtime resolution uses approved primitive
facts, ignores malformed direct-configured audience templates, and emits no
event or application-policy change. The public scoped-capture guide holds the
normative contract.

Python 3.14 guards cover audience selection, shared fallback, invalid profile
and template rejection without partial provider registration, and a direct
malformed template with an opaque value. The old source failed the audience
and validation guards; the new source passes them alongside existing capture
and provider contracts.

## Scope

This is an opt-in provider capability. Recorda owns any subsequent adoption
or presentation change, and the current rich and shared metadata templates
retain their behavior. It does not authorize arbitrary rendered text as safe.
