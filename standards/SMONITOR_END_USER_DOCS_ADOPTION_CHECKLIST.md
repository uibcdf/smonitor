# Adoption Checklist: End-User Diagnostics Docs in Library A

Use this checklist when integrating SMonitor into library `A`.

## Mandatory in A docs

- [ ] Add a user-facing section: "Diagnostics in A (powered by SMonitor)".
- [ ] Include interpretation of `WARNING` vs `ERROR`.
- [ ] Include 30-second rescue flow.
- [ ] Include issue-report payload requirements.
- [ ] Link to extended SMonitor end-user docs.

## Mandatory A-specific customization

- [ ] Add at least one common code ID example from `A`.
- [ ] Add `A`-specific verbosity/diagnostics instructions.
- [ ] Add `A` issue tracker link.

## Source alignment

- [ ] Section is based on `SMONITOR_END_USER_DOCS_TEMPLATE.md`.
- [ ] Local copy includes sync metadata (`Synced from: smonitor@...`).
- [ ] Local copy reviewed against latest `SMONITOR_END_USER_GUIDE_FOR_LIBRARIES.md`.

## CI/maintenance (recommended)

- [ ] Add a docs check in `A` CI verifying the section exists.
- [ ] Add periodic review task for doc sync (for example once per release).
- [ ] When SMonitor docs change, re-sync `A` copy and update sync metadata.
