---
summary: Qualify and publish explicit binding and bounded observation in SMonitor 0.23.0.
issue: uibcdf/smonitor#67
status: active
opened: 2026-11-10
verification: measured
area: [release, profiling, packaging]
guard: tests/test_noarch_conda_publication.py
normative: devguide/conda_release_routes.md
blocked_by: []
supersedes: []
---

# SMonitor 0.23.0 publication

Diego authorized resolving #63–#66 and publishing a new release, with direct
main commits and pushes. The advance impact notice is uibcdf/molsyssuite#181.
The starting main source is c1b6ce29c3729b99429b395a00c7866a759be406.

## Route and qualification

Use staging for these additive observation and explicit binding surfaces. Keep
the immutable v2.3.0 build/inspect/separate-upload provider and the exact-file
promotion route already qualified for 0.22.1. Build number starts at zero only
once independent all-label registry absence is verified. Do not overwrite tags,
files or original receipts. Create canonical tag and GitHub Release title
exactly 0.23.0 after the exact candidate and staged file gates pass.

The existing package supports Python 3.11–3.14 on Linux x86_64/macOS arm64/Windows.
The new call backend is explicitly CPython 3.12–3.14 with the GIL; process-family
and capacity observation is explicitly Linux /proc. Negative capability tests
execute alongside the existing diagnostics on unsupported cells. Source and
installed twelve-cell gates retain those exact support/omission boundaries.
Required source collective E2E/bootstrap remains separately executed in QA.

Retain actual installed files, CLI, final provenance, scientific/regression
results, matrix cells and original producer/upload/promotion receipts. Verify
public main/index/hash independently and run fresh public installed receiving
outside the checkout before final notifications and cleanup.

## Local checkpoint and environment limits

Routine source uses Python 3.14.7 from molsyssuite@uibcdf_3.14. The shared prefix
has existing unrelated pip-check conflicts (missing pdb2pqr and incompatible
NumPy/Biopython/provider requirements) and an editable Pytest Receptor. Preserve
that prefix. Local runs use a task-owned overlay of published Pytest Receptor
1.2.1, downloaded as its public wheel, with actual SMonitor source imports.
These source results are scoped independently from the later clean installed
qualification and required hosted environments. No healthy shared-prefix or
unrelated-client compatibility claim is made.

The documentation build initially reported five root-page H2-without-H1
warnings. Its missing document title was restored during release qualification.
The generated source `_version.py` was refreshed with versioningit's supported
write operation after an older ignored build file was observed locally.

## Archival applicability

SMonitor's registered archival mode is optional. This release does not elect a
new DOI/archival route; retain the previously verified 0.16.0 source milestone
as historical evidence. Source/GitHub/Conda delivery claims require their own
receipts. Any later elected or observed exact-version archival needs its public
record/file verification and the canonical recovery route before a DOI claim.

## Closeout

After verified publication, update the version-specific notice in MolSysSuite,
notify MolI and concrete consumer owners, hand guide-only synchronization to
MolSysSuite, retain sanitized evidence and retire task-owned resources. Archive
this report and regenerate indexes only when the release outcome is known.
