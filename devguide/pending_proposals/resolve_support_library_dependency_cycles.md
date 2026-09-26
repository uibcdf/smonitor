---
summary: Resolve ArgDigest and DepDigest dependency cycles at SMonitor boundaries.
issue: uibcdf/smonitor#29
status: open
opened: 2026-09-26
closed:
verification: inspected
area: [architecture, ecosystem, dependencies]
guard:
normative: MOLSYSSUITE_GUIDE.md
blocked_by: []
supersedes: []
---

# Resolve support-library dependency cycles

The completed member review in `uibcdf/smonitor#24` found two applicable
support-library boundaries. Public configuration and event validation are
ArgDigest-shaped; the optional `rich` console backend is DepDigest-shaped.
ArgDigest depends on DepDigest and SMonitor, while DepDigest depends on
SMonitor. A runtime dependency in the reverse direction would create a cycle.

The temporary exception keeps SMonitor's bootstrap validation and lazy
optional-backend handling local. Its owner is the SMonitor maintainers and its
expiry is 2027-03-26. The central MolSysSuite inventory tracks the same
exception as `support-libraries=excepted`; this is not an adoption claim.

Before expiry, choose a cycle-free dependency structure or obtain a revised
applicability rule through MOLI and MolSysSuite governance. Verify the chosen
contract with public validation, optional-backend, installation and import-order
tests. Remove the exception only after that evidence is published and the
central inventory is updated.
