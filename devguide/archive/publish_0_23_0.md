---
summary: Qualify and publish explicit binding and bounded observation in SMonitor 0.23.0.
issue: uibcdf/smonitor#67
status: resolved
opened: 2026-11-10
closed: 2026-11-10
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

## Verified outcome — 2026-11-10

Provider issues #63–#66 are resolved with maintained contracts and executable
regression guards. The immutable tag and stable GitHub Release `0.23.0` identify
`ed3231c51d66d8c51d8ca8a1a798ded07a40952c`. Publication time is
2026-11-11T03:42:43Z (2026-11-10 locally). Required runtime providers remain
empty, optional floors remain unchanged and installed MIT notice/metadata
agree with the declared source.

All twelve source cells in run 42949342319 and all twelve installed cells in
42951310668 pass. Candidate CI, QA, Docs and policy pass; QA executes required
collective E2E/bootstrap. Independent installed validation verifies the exact
archive, candidate, attempt, matrix and required executed steps. The optional
nightly-decision job is deliberately skipped on manual dispatch. Unsupported
new observation backends have explicit refusal controls, while diagnostics
retain their existing support. No required installed step is skipped.

Isolated Python 3.14.7 source qualification reports 913 passed / four scoped
skips, a clean pip check and branch coverage 1224/1328 (92.1687%). The retained
prefix's package metadata predates the final source commit/tag; these are
source-checkout results, independently qualified from installed package bytes.
Ruff/format, report indexes and Sphinx with zero warnings pass.

Producer 42950020732 builds/tests once, inspects and separately uploads the
exact `smonitor-0.23.0-py_0.tar.bz2`, SHA-256
`32f6bff5056a2af967caf676840b4b65ba0e9d370879637cfd60579681755e35`.
Promotion 42955042087 adds main to that same staged file. Original producer
events correctly record upload as not requested in the build-only operation;
the separate upload receipt proves delivery. The stable release event executes
the staged guard and deliberately skips duplicate build/upload operations.
Tag policy and release documentation deployment also pass.

Hosted and independent public main-label/solver-index/digest verification pass.
A fresh minimal public Conda prefix outside the checkout uses Python 3.14.10
and only SMonitor plus pip as Python distributions. It passes installed identity,
explicit binding/application policy, selected Python/native call identity and
error controls, process-root refusal, actual child/sibling sampling and cleanup,
three installed CLI help commands and pip check. Its family observation has zero
read failures; the report preserves sampled/partial fields and unavailable true
peak rather than implying continuous coverage.

Sanitized original receipts, native snapshots, installed descriptor/binding,
public receiving control and checksums are retained in
`devguide/validation/data/release_0_23_0/receipt.json`. Historical disposable
paths identify the environments used; no other prefix or cache is modified.
A local `/tmp` quota failure during fresh receiving setup was recovered by
retiring only completed task-owned resources and placing the disposable Conda
cache under an owned ignored build child. No hosted gate was waived.

The formal version-specific notice is uibcdf/molsyssuite#183; advance impact is
#181 in that repository. MolSysSuite owns canonical-guide delivery through #165,
selecting the refreshed registry rather than assuming the older client count.
MolI direct-consumer review remains uibcdf/moli#82; concrete receiving remains
with uibcdf/opencastp#13, uibcdf/pharmacophoremt#98 and uibcdf/pyunitwizard#141.
PyUnitWizard's separate negative-probe improvement is already closed in 0.29.2;
SMonitor binding availability does not reopen it or prove a whole-workload gain.
No sibling worktree, consumer pin, scientific policy or resource-allocation
infrastructure is changed by this provider publication.
