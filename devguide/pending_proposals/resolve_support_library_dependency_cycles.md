---
summary: Resolve ArgDigest and DepDigest dependency cycles at SMonitor boundaries.
issue: uibcdf/smonitor#29
status: blocked
opened: 2026-09-26
closed:
verification: inspected
area: [architecture, ecosystem, dependencies]
guard:
normative: MOLSYSSUITE_GUIDE.md
blocked_by: [uibcdf/moli#29]
supersedes: []
---

# Resolve support-library dependency cycles

## 2026-09-26 governance checkpoint

The dependency graph still has `argdigest -> depdigest -> smonitor` and a direct
`argdigest -> smonitor` edge. The alternative of retaining SMonitor diagnostics
inside those providers while adding either as a required SMonitor dependency
cannot satisfy the cycle-free acceptance criterion. SMonitor's existing local
validation and lazy backend handling remain the bounded exception, with no
claim that the inherited policy has changed.

MOLI owns cross-component applicability. `uibcdf/moli#29` now asks whether a
narrow rule for diagnostic bootstrap providers is appropriate, or whether the
providers must remove the reverse runtime edges. The central MolSysSuite
inventory remains `excepted` until that normative decision is effective and
the public-boundary, installation and import-order evidence below passes.
This report is blocked on that decision; neither closing it nor advancing the
inventory would be accurate yet.

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
