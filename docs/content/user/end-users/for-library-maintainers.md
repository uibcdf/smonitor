# End-User Documentation Pack for Library Maintainers

This page is for maintainers of a host library integrating SMonitor and needing
a clear end-user section in host-library docs.

## Why this is necessary

Without a short user-facing guide in the host library, diagnostics can feel like external
noise. With a guide, users treat messages as task support.

## Recommended hybrid strategy

1. Embed a short first-contact/rescue section in host-library docs.
2. Link to SMonitor extended end-user docs for deeper guidance.

## Canonical sources to copy from

- `standards/SMONITOR_END_USER_GUIDE_FOR_LIBRARIES.md`
- `standards/SMONITOR_END_USER_RESCUE_CARD.md`
- `standards/SMONITOR_END_USER_DOCS_TEMPLATE.md`
- `standards/SMONITOR_END_USER_DOCS_ADOPTION_CHECKLIST.md`
- `standards/SMONITOR_END_USER_DOCS_SYNC_POLICY.md`

## Minimum content for host library docs

1. Meaning of `WARNING` vs `ERROR` in the host library.
2. 30-second rescue flow.
3. How to report issues for the host library (tracker URL + payload).
4. Whether the host library exposes verbosity/profile controls.
5. Link to extended SMonitor end-user docs.

## Versioning advice

- keep a copied section in the host library for immediate usability,
- link to SMonitor online docs as the continuously updated reference.

## Recommended operational workflow

1. Copy template from `SMONITOR_END_USER_DOCS_TEMPLATE.md` into host-library docs.
2. Fill host-library-specific placeholders (codes, verbosity controls, issue URL).
3. Validate with `SMONITOR_END_USER_DOCS_ADOPTION_CHECKLIST.md`.
4. Add sync metadata in the host library copy (`Synced from: smonitor@...`).
5. Re-sync periodically following `SMONITOR_END_USER_DOCS_SYNC_POLICY.md`.
