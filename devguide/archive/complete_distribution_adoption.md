---
summary: Maintain distribution-route controls and qualify each claimed installed cell.
issue: uibcdf/smonitor#35
status: resolved
opened: 2026-10-06
closed: 2026-10-06
verification: measured
area: [governance, distribution, compatibility]
guard: tests/test_distribution_inputs.py
normative:
blocked_by: []
supersedes: []
---

# Distribution route and runtime review

**Reported:** 2026-10-06, central uibcdf/molsyssuite#45 review.

## What

Maintain controls for every public/source/build route, preserving the local
noarch publisher and original public release bytes. Source matrix execution,
installed-file qualification and current-source governance are separate claims.
The maintainer chose to complete installed evidence through the new 0.19.0
release rather than dispatch tests for historical 0.18.0.

## How

Use the general @2 inventory at `devtools/dependency_routes.toml`: one local recipe,
five environments and nine workflows. The thin entry point delegates parsing,
constraints, resource review and native gate acquisition to MolSysSuite
**25363f2a2c902c04b2cdc8b301a3e1c1ff0c0918**. That immutable provider passes
78 focused local checks and native governance run 37507549797 with 368 tests
and its dependent coverage upload. Existing @1/@2 consumers retain their pins.

No required Python dependencies exist. Required sibling-floor/source replacement
cases are inapplicable with a reason; optional pytest bridge and collective
integration retain distinct evidence. Runtime test environments preserve Python
>=3.11,<3.15; development/docs select 3.14 within that range. Parser requirements
are developer tools, also present in future installed test environments.
Recipe host tools match declared setuptools/wheel requirements and versioningit
3 series. Bootstrap versioningit stays in that series. Docs runtime channels
retain strict UIBCDF/Conda-forge priority; build-only bootstrap stays classified.

Default early source/QA/collective/docs jobs inspect routes, source resources
and actual installed public bounds. Documentation triggers cover modified inputs.
The full source matrix retains its twelve cells and schedule/backlog/manual
triggers. Future candidate build and promotion checks require the exact source,
all twelve executed full-matrix jobs and common policy, including distribution
input checks. Backlog-only green is insufficient. A separate receipt records
these candidate proofs before publication mutation.

Retain the release team's ten-path resource inventory, shared installed workflow,
all twelve installed cells and final installed provenance checks. Prospective
recipe tests also check the two installed namespace template payloads. Existing
version freezer, immutable-coordinate controls, installed verification and
same-byte promotion/public poststate remain intact. No parser or artifact engine
is copied into this component and no runtime/scientific implementation changes.

## Why

Archived release receipts alone cannot protect later route/resource drift. The
initial public 0.18.0 Windows command smoke did not certify a complete installed
matrix or the later provider APIs. The new release supplies that missing artifact
evidence while maintained controls protect future development and releases.

## Measured scope

Prepared controls first targeted clean source 6feac9728cc35d57cbc92f284d7040d7f04cb35b,
with 149 selected local tests and two unresolved-report skips. Work paused for
owner publication. The reviewed integration now starts from released source
**f604b940ab281df4554869fdd24f796ea6d42c27**, retaining owner #37/#38 work and
both subsequent release commits. The primary developer clone stays intact.

Qualified environment `molsyssuite@uibcdf_3.14` uses Python 3.14.7; primary
Pytest Receptor and GH Run Receptor origins are verified. Seven existing closure
findings remain central #82 debt. The default operation passes all 15 routes,
source resources and current installed public Python bounds. Current selected checks pass **151 tests / two unresolved-report skips**.
Four isolated current-input mutations are rejected: missing recipe Python, wider
runtime Python bounds, missing shipped template and wrong generated-version target.
Applicable hosted source/QA/docs/policy execution is recorded when complete. Required Ruff 0.16.5, indexes and whitespace are separate gates.

## Original public artifact evidence

Release 0.19.0, build 1: `noarch/smonitor-0.19.0-py_1.tar.bz2`, SHA-256
**4b876b4993b1e2caeed40851402a931f3b245ed7c1916d9483d81bc90274e31c**;
original producer/source **f604b940ab281df4554869fdd24f796ea6d42c27**,
producer 37520722817, source matrix 37520498547, installed matrix 37521323117,
public promotion 37522036404. The release owner incremented the build after an
installed test assertion failed in build 0; that staged coordinate was preserved.
Central review independently checks the downloaded public hash, embedded version,
metadata, ten resources, executed source jobs, all twelve installed cells and
the promotion receipt ZIP digest using maintained shared operations. Matrix
validation names every executed installation/resource/test/final-provenance step.
No rebuild, promotion, overwrite or new scientific execution follows this review.

Original 0.18.0 producer b79cca8eb9bd878d0d3439876eca4ed26560e916 and hash
7fba29b56853771ceaf477de50aeed0cf9e93e2053e484de4e18c18ea1abe578 remain
historical evidence in the initial central receipt; they are not relabelled as
qualification of later APIs or a twelve-cell matrix.

## What was refuted

- Replacing the maintained local publisher only to fit shared orchestration.
- Overwriting release 0.19.0 resources or installed gates with the earlier draft.
- Inventing required sibling floors for optional tooling.
- Treating declaration-only or backlog aggregate success as executed qualification.
- Creating a namespace __init__ file to fit an incorrect resource inventory.
- Rebuilding a public archive to finish governance adoption.
- Qualifying current capture APIs through the old public 0.18.0 artifact.

## Remaining work and acceptance

- Inspect applicable exact-head source/QA/docs/policy execution and retain counts,
  skips and any failures without treating them as installed artifact evidence.
- Retain current early-route negative checks, future exact-candidate gates,
  original public qualification and independent current public availability.
- Archive only when maintained controls and formal member review are complete.

## Guard relevance

`tests/test_distribution_inputs.py` rejects changed provider identity, incomplete
native profiles, offline-proof misuse, wrong candidate source and hidden provider
failures. It checks early invocation/publication ordering, separate optional scope,
installed-template recipe tests and declared build requirements. Maintained shared
route/resource/archive negative guards and existing local freezer/release guards
remain relevant and addressable. Hosted evidence is recorded separately.

## Resolution — 2026-10-06

Implemented at **169d070b2b0894eb452c5a962db5757b92f202f8**. Exact-head native
CI 37529262021 and QA 37529261919 both execute the 15-route/default installed
bounds review before **631 passing tests / five skips**. Two skips represent
unresolved reports (including this report before closure); unavailable optional
provider/sibling evidence remains visible. Collective QA independently executes
three tests, strict QA seven, and wheel/CLI packaging smoke succeeds. Docs
37529261976 executes the same early review and builds successfully with five
warnings. Common policy 37529262843 passes all three mandatory checks. GH Run
Receptor captures complete metadata/jobs/steps/logs for each exact native attempt.

The original public 0.19.0 archive and its twelve-cell qualification are verified
independently as recorded above, with **617 passing tests / four skips per
installed cell**. Those historical scientific selections are not replaced by the
new governance test module. The downloaded hash and promotion receipt identify
the same original bytes. No new full/installed matrix, package build or public
mutation is executed by the central review. Future candidate source requirements
are prospective; this adoption does not assert a new release at 169d070.

The local guards protect provider identity/cleanliness, complete native job
profiles, candidate identity, qualification labels, provider failures, early
workflow ordering, installed templates and build-tool metadata. Four controlled
current-input mutations independently fail through maintained provider operations.
This meets the review acceptance while preserving required-dependency
non-applicability, optional integrations and local publication ownership.

Central adoption and artifact receipts are coordinated in uibcdf/molsyssuite#45;
provider API adoption stays separate in uibcdf/molsyssuite#106. Closing this member
review does not qualify another consumer or guarantee future publication access.
