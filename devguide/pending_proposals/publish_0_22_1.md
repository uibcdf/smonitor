---
summary: Qualify and publish the 0.22.1 correction release through staging.
issue: uibcdf/smonitor#62
status: active
opened: 2026-11-04
closed:
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
