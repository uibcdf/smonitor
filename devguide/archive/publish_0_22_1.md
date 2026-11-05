---
summary: Qualify and publish the 0.22.1 correction release through staging.
issue: uibcdf/smonitor#62
status: resolved
opened: 2026-11-04
closed: 2026-11-04
verification: measured
area: [release, packaging, interoperability]
guard: tests/test_noarch_conda_publication.py
normative: devguide/conda_release_routes.md
blocked_by: []
supersedes: []
---

# SMonitor 0.22.1 publication

Diego authorized publishing the completed fixes after source issues #54, #55,
#57, #58, #59 and #61 were resolved. Direct main commits/pushes remain authorized.
The starting source is ccdcace55ba5caf431b4a6a6904d8d18173114a3. Prior source
and private-wheel evidence remains scoped to those owner records.

The reviewed route is staged because SPDX/backend metadata and the immutable
v2.3.0 separate-upload provider changed. A patch version or pure-Python payload
alone does not qualify a direct upload. The new coordinate was independently
absent from Anaconda at preparation. No historical tag/file is replaced.

The committed plan retains twelve source and installed cells: Linux, macOS
arm64 and Windows on Python 3.11--3.14. Routine local work uses Python 3.14.
Rich 15.0.0 is an explicitly public qualification tool in source/QA/installed
environments, not a new runtime dependency. Cross-repository E2E and bootstrap
integration retain their separate source-owned QA scope; package-only evidence
does not qualify those missing optional clients.

Before tagging, require the exact final candidate's full matrix, policy, QA
build/license/sdist-rebuild/CLI and docs checks. Build/test once, inspect actual
version/resources/notices, upload only the exact inspected staging file, and
independently verify its digest. Qualify that installed archive on all twelve
cells with launcher, regressions and final provenance before publication.

Create immutable tag 0.22.1 and a stable GitHub Release titled exactly 0.22.1.
Promote the same file/digest only after those gates; independently inspect main
label, solver index and clean public receiving. Preserve original failed attempts
and use additive repairs for defective candidates. The owner issue and final
receipt retain actual candidate/run/attempt/job/file identities; no run IDs or
self-referential SHA belong in the committed release plan.

Close only after retaining public delivery evidence, coordinating guide/consumer
receiving and retiring task-owned temporary resources. The guard protects the
stage/installed/promotion order and exact-file/digest wiring; executed release
receipts remain distinct from structural contract tests.

## Measured publication, 2026-11-04

The immutable tag and stable GitHub Release
[0.22.1](https://github.com/uibcdf/smonitor/releases/tag/0.22.1) identify
2147c7c641b7cba8a974b193207f686ee3ebe855; the release title is exactly 0.22.1.
The twelve-cell [source matrix](https://github.com/uibcdf/smonitor/actions/runs/41957914786),
policy, QA and docs pass at that source. Both pinned preflights independently
verify the required native jobs/steps and fifteen distribution input routes.

The [producer](https://github.com/uibcdf/smonitor/actions/runs/41960261508)
built and tested one noarch archive, inspected it before separate exact upload,
retained original build/upload evidence, and passed the Windows launcher smoke.
Actual metadata and notice checks preserve SPDX MIT and the original LICENSE
bytes. Required runtime providers remain empty and optional floors agree with
the reviewed package declarations.

All twelve [installed cells](https://github.com/uibcdf/smonitor/actions/runs/41961945246)
pass against smonitor-0.22.1-py_0.tar.bz2, SHA-256
e9ce6c77a682dddec3a6e724f9cc98cca31c4d6732453d554107ffcf61f23e7e.
Each cell executes 812 passing tests with four scoped skips: source-only
optional-client integration and active-report bookkeeping. Required collective
E2E/bootstrap integration executes separately in QA; installed files, launcher,
scientific test step and final import provenance are executed in every cell.
This does not qualify every client workflow or unknown future provider versions.

The [release event](https://github.com/uibcdf/smonitor/actions/runs/41970738259)
passed staged routing without rebuilding or uploading again. Exact-file
[promotion](https://github.com/uibcdf/smonitor/actions/runs/41970853019) passed;
hosted and independent pinned verifiers confirm main-label and solver-index
digest equality. Staging remains as a second label on the same file. A fresh
public Python 3.14 Conda prefix outside source passes nine signal/callback/
capture controls and three CLI checks, with actual installed origin and the
same public file hash verified.

[Retained receipts and frozen receiving control](../validation/data/release_0_22_1/receipt.json)
preserve original producer/upload/promotion/native-matrix/public verification
documents byte-for-byte, their SHA-256 values, qualification scope and actual
public receiving. The original source run's ten passing cells and two unstarted
cancelled macOS jobs remain historical evidence after one bounded requeue.
An eighteen-repository snapshot found five macOS runners occupied and 51 queued
jobs, matching the normal Free-plan cap; a private support override was not
inspected and no foreign run or quota setting was changed.

The canonical guide digest is recorded for central delivery in MolSysSuite #165.
Client source/public/scientific receiving remains separately owned under #163.
The final issue closeout records retirement of task-owned temporary prefixes and
caches after receipt retention; historical paths in the receiving record do not
claim that those resources remain active.
