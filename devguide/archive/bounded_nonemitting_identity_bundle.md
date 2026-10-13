---
summary: Evaluate bounded nonemitting support-bundle export for strict consumers
issue: uibcdf/smonitor#40
status: resolved
opened: 2026-10-13
closed: 2026-10-13
verification: reproduced
area: [bundle, capture, support]
guard: tests/test_identity_bundle.py::test_identity_bundle_omits_unreviewed_payloads_and_top_level_sections
normative: docs/content/user/bundles-and-export.md
blocked_by: []
supersedes: []
---

# Bounded nonemitting identity bundle

## What and why

Recorda's diagnostic-correlation analysis (uibcdf/recorda#15) found that rich
`collect_bundle()` includes top-level `argv` even when event extras and
messages are dropped or redacted. It also flushes pending summaries, which
can deliver new diagnostic events. Those behaviors are part of the rich
support-bundle contract and are unsuitable for a controlled strict consumer.

## Resolution

The bundle owner now supplies `collect_identity_bundle()` and
`export_identity_bundle()` as separate public tools. They only read retained
events; neither calls `report()`, reads project configuration, flushes pending
summaries nor invokes handlers. The versioned artifact contains fixed
provenance, bounded coverage counts, explicit omitted sections and at most
100 selected event rows. Rows contain only a validated level, a 16-character
fingerprint and a code if the caller approved that exact bounded code in an
explicit allowlist. The allowlist accepts at most 128 identifiers.

The artifact always reports incomplete historical coverage: previous buffer
eviction, filtering and pending summaries cannot be reconstructed. It is an
identity/correlation sidecar, not a universal sanitizer or a promise that
fingerprints cannot be guessed. Rich `collect_bundle()` and `export_bundle()`
retain their schema, defaults and redaction behavior. The public bundle guide
documents the opt-in contract and its limits.

The Python 3.14 guard uses synthetic argv/config/message/source/extra canaries
and checks the full exported key set, nonemission and approved code. Other
guards check selection limits, omitted codes, pending-summary behavior and
file overwrite protection. Consumer adoption remains with Recorda and the
cross-component coordination in uibcdf/moli#62.
