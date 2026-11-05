---
summary: Support src layouts and explicit package roots in integration audits.
issue: uibcdf/smonitor#54
status: resolved
opened: 2026-11-04
closed: 2026-11-04
verification: measured
area: [maintenance, contracts]
guard: tests/test_verify_integration.py
normative:
blocked_by: []
supersedes: []
---

# Integration audit package roots

The audit assumed repo/repo.name and rejected valid src layouts reported by
uibcdf/peptidemt#6. It now discovers either conventional flat or src package
roots, rejects missing/ambiguous roots, and accepts --package-dir for one
explicit repository, relative to that repository or absolute. An explicit
choice supports different checkout/package names. It cannot be mixed with --all.

Seventeen audit tests pass, including real configuration/template/rendering checks
for a src fixture, ambiguity, missing roots, overrides and prior probe custody.
PeptideMT is not checked out locally; no receiving run on that repository is
claimed. The canonical guide also corrects its import recipe: CATALOG stays in
the private module; _smonitor.py imports only CODES and SIGNALS. Catalog import
has not become a supported top-level configuration key. Source/guide delivery
is handed to the existing central guide coordination; runtime floors stay local.
