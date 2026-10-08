---
summary: The integration verifier deletes caller-owned probe modules.
issue: uibcdf/smonitor#43
status: resolved
opened: 2026-10-08
closed: 2026-10-08
severity: medium
verification: reproduced
area: [devtools, resources]
guard: tests/test_verify_integration.py::test_probe_restores_caller_namespace_on_every_exit
normative:
blocked_by: []
supersedes: []
---

# The integration verifier deletes caller-owned probe modules.

## What

At c7bfb0b69b4f26e140c5b1668db76c3174b3f2b7, load_catalog removes
caller-owned sys.modules entries under its synthetic probe prefix. A previously
loaded relative helper can also contaminate the source being reviewed.

## How

A real catalog on an owned filesystem fixture reproduces loss of a pre-existing
ModuleType sentinel. The durable guard covers occupied/empty namespace against
successful load, diagnosed ValueError and propagated KeyboardInterrupt. It
checks exact restored module identities, absence of operation-created imports,
fresh relative helper source and unchanged caller fixture files. Three occupied
cases fail before repair; three empty-namespace controls pass.

## Why

This developer-tool resource defect is local to SMonitor, found during
uibcdf/molsyssuite#104. Integration verification must not destroy prior imports
or use another probe's stale source. Runtime catalog/signal/serialization APIs
and installed consumer dependencies are unchanged.

## What was refuted

This is not a filesystem leak or a need for global sys.modules cleanup. Existing
synthetic loading remains the owning reusable operation; save/isolate/restore
only its namespace in its existing try/finally. Catalog fixtures deliberately
reject importing their scientific package root. Thread-safe global import
mutation is not established by this synchronous tool review.

## Resolution

Snapshot and detach prior probe entries inside the protected load, then remove
operation imports and restore exact prior identities in finally. Guard exercises
success, failure and interruption on real fixture imports; before/after proof
establishes relevance. Source/full hosted evidence and closeout are linked in
the owning issue. Historical resources and installed matrices remain separate.

Qualified Python 3.14.7: all 653 ordinary source tests pass with two explicit
skips (one collective sibling case absent in isolated workspace, one reported
without resolved reason by the receptor). The unchanged central provider
25363f2a2c902c04b2cdc8b301a3e1c1ff0c0918 verifies fifteen declared-and-installed
public-bound routes. Both probe helps, whole-repository Ruff (126 formatted
files), local report/index checks and central offline governance guard pass.
No public package/installed matrix, solver or deferred scientific suite invoked.
Native exact-source gates and source-only operator notice delivery are retained
in the owning issue and central #104 receipt before board closeout.

### Skip clarification — 2026-10-08

The literal "not resolved" skip is intentional in
`test_a_resolved_report_names_a_guard_or_a_normative_document`: a non-resolved record does not require a
resolved guard. Source inspection identifies its reason; no receptor defect or
missing source-test evidence is inferred from that label. The other skip is the
explicitly absent collective sibling fixture.
