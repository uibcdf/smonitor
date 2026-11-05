---
summary: Adopt provider v2.3.0 with inspection before exact-file upload.
issue: uibcdf/smonitor#58
status: resolved
opened: 2026-11-04
closed: 2026-11-04
verification: measured
area: [maintenance, contracts]
guard: tests/test_noarch_conda_publication.py
normative:
blocked_by: []
supersedes: []
---

# Conda provider v2.3.0 owner review

Review completed for build, upload and promotion against immutable provider
87c70b1443d5f22d738ee3ddf812bdbe0152f6c2 and central delivery
95f693be10c9205ab9b912cb53453710a207bf45 (uibcdf/molsyssuite#87).
The component retains its local publisher/profile; it does not switch to a
shared workflow or change release triggers and authorization.

The old combined action could not inspect built bytes between build and upload.
Both source paths now build with upload:false, inspect the single original
archive with the already pinned noarch tool, and pass that exact filename,
candidate and digest to the separate immutable upload operation. Build outputs
and producer evidence remain bound to their original step IDs. Archive inspection
and upload receipts are retained alongside existing route receipts. No conversion
is requested, so noarch remains host-only; --package-format 1 explicitly requests
tar.bz2. Unneeded deprecated mambabuild:false is omitted. No force/overwrite is used.

Promotion uses the same immutable provider's exact coordinate/label/digest
operation after the existing twelve-cell installed verification. Independent
public verification remains after publication. Reviewed workflow hashes are
updated in the local dependency-route inventory. Contract tests guard ordering,
upload:false and exact artifact/digest wiring, plus existing source/installed/
public gates. No workflow dispatch, registry write, rebuild, promotion or public
release was performed by this owner review; live operation of a future candidate
remains a separate qualification, not inferred from these source checks.
