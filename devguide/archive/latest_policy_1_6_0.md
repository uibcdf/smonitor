---
summary: Receive policy 1.6.0 with a matching reviewed workflow digest and bounded resource profile.
issue: uibcdf/smonitor#68
status: resolved
opened: 2026-11-16
closed: 2026-11-17
verification: measured
area: [governance, ci]
guard: tests/test_distribution_inputs.py::test_reviewed_provider_checkouts_and_workflow_bytes_match_inventory
normative: MOLSYSSUITE_GUIDE.md
blocked_by: []
supersedes: []
---

# Policy 1.6.0 and reviewed workflow receiving

## What

Receive the latest immutable policy target through the existing owner issue,
with current common/root/nested instructions, canonical guides and the scoped
resource disposition requested by MolSysSuite #201/#197. Older public releases,
scientific/provider/artifact identities and their evidence retain their dates.

## How and observed defect

The actual caller still selects policy-v1.5.4; the real frozen checker
reports LATEST_POLICY. Update that single caller to immutable policy-v1.6.0
and update only its corresponding workflow digest in
`devtools/dependency_routes.toml`. The matching digest is
7000a5b495c77a7dbceedfd4f1089df6919ab576169747bfe9047e3acc103da9.
The accepted distribution SDK 6d6172d6cd00c5ac2d4ebadb71df554ec5b7fa26,
all other provider/publication pins and runtime/API/catalog code are preserved.
No public release, package or canonical SMonitor guide revision is selected.

## Why and executed checks

A current caller and an old declared workflow digest contradict the existing
source/distribution guard. Refreshing the reviewed digest preserves that guard;
removing it or changing the accepted SDK is unnecessary. The actual frozen
1.6.0 source is 698fbdfd4b0a53b6b7cc49815e1102cd9c117749, annotated object
4d20cfc2e6d2aff783561410f23f69d660bca92e. Registration already covers this
member; no admission input is needed. Current canonical relationships are
checked with the official synchronizer. It receives only the newly published
common guide; the source-owned tool guides remain unchanged.

The existing selected tests pass with published Pytest Receptor 1.2.3:
232 initial cases covering administrative and applicable public/API contracts.
The real frozen checker has zero findings after repair. Ruff lint/format pass
in the hydrated source context. Early OpenCASTp sparse-context import ordering
warnings disappear after real package sources are hydrated, without a numerical
or import-order edit. Native check exits and original failed attempts remain
in the receiving evidence; repeated executions are not additive coverage.

## Resource profile and limits

Load the common resource action and relevant local instructions before work.
This selected engineering task uses one material job, one inherited CPU,
nice 10/native threads 1, estimated 1 GiB RAM / 384 MiB task scratch, per-process
AS 2 GiB / CPU 60 s and owned-session wall 180 s with one-second observations and
a 13 GiB available reserve. Available memory and per-process limits establish
neither a reservation nor aggregate RAM protection or concurrent admission.
No site scheduler/admission policy is advertised to this task. Unknown larger
scientific/native/GPU/browser/installed workloads retain their owner profiles.

## Scope and exclusions

Runtime behavior, scientific definitions, native build outputs, installed/public
claims and all independently pinned SDKs are unchanged. No shared-prefix
installation, native build, benchmark, package upload or manual workflow
dispatch is selected. Ordinary configured CI retains its own actual outcomes.
Keep unexecuted/failed/omitted gates explicit, preserve other owners' useful
scratch and remove only this task's marked scratch after durable receiving.

## Acceptance and delivery

The candidate is locally reviewable. Delivery uses an owner-reviewed PR; default-branch integration and exact-source
hosted evidence remain pending their actual outcomes. Close only after published
source, actual applicable checks and owner disposition are returned here and
to central #201/#197; original scientific/installed/public criteria stay owned.
The registered guard checks reviewed workflow integrity; latest policy itself
is separately enforced by the frozen checker and live adoption inventory.


## Final candidate evidence

The [local receipt](../validation/policy_receiving_68_20261117.json) records exact commands and failed attempts.
The final selected candidate has 236 passing cases and no skipped guard.
Source publication and actual hosted/central receiving remain separate pending
steps; numerical/runtime/installed/public qualifications are not inferred.


## Contribution route and canonical clarification

Diego confirms owner-local direct pushes and ordinary issue/PR review in another
UIBCDF repository without an extra publication-permission round. Mandatory prior
permission applies to third-party issue/PR publication outside github.com/uibcdf.
The official synchronizer receives common guide SHA256
d256eaba4523a0535bf810d9177184e5b1791f797baf6d3218f847fb316b29b5 from published
central a02f2b463d4100b804252130b903ad7b09b0cad6. Other guide/SDK/runtime inputs
are unchanged by this proposal. This archived resolution is the proposed merged
state: the owning issue stays open while its PR awaits owner review/integration.
Branch publication does not establish adoption on the default branch.
