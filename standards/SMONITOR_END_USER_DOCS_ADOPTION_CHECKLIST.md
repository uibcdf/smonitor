# Adoption Checklist: End-User Diagnostics Docs in Host library

Use this checklist when integrating SMonitor into a host library.

## Mandatory in Host-Library Docs

- [ ] Add a user-facing section: "Diagnostics in <Host Library> (powered by SMonitor)".
- [ ] Include interpretation of `WARNING` vs `ERROR`.
- [ ] Include 30-second rescue flow.
- [ ] Include issue-report payload requirements.
- [ ] Link to extended SMonitor end-user docs.

## Mandatory Host-Library Customization

- [ ] Add at least one common code ID example from the host library.
- [ ] Add host-library-specific verbosity/diagnostics instructions.
- [ ] Add host library issue tracker link.

## Source alignment

- [ ] Section is based on `SMONITOR_END_USER_DOCS_TEMPLATE.md`.
- [ ] Local copy includes sync metadata (`Synced from: smonitor@...`).
- [ ] Local copy reviewed against latest `SMONITOR_END_USER_GUIDE_FOR_LIBRARIES.md`.

## CI/maintenance (recommended)

- [ ] Add a docs check in the host library CI verifying the section exists.
- [ ] Add periodic review task for doc sync (for example once per release).
- [ ] When SMonitor docs change, re-sync the host-library copy and update sync metadata.
