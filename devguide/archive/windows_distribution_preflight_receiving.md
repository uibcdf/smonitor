---
summary: Windows rejects the shared distribution preflight before source tests.
issue: uibcdf/smonitor#46
status: resolved
opened: 2026-10-09
closed: 2026-10-09
severity: medium
verification: reproduced
area: [distribution, ci, windows]
guard: tests/test_distribution_inputs.py::test_reviewed_workflow_bytes_survive_autocrlf_checkout
normative:
blocked_by: []
supersedes: []
---

# Windows distribution preflight receiving

**Reported:** 2026-10-09, original daily full matrix 37935661439 at
`7ed94f1677965b0281c883dda784fd480be42c29`.

## What

All four Windows Python 3.11–3.14 source cells stop at `Check distribution
inputs`, before package installation/tests. Linux/macOS cells pass. The original
error compares `devtools\conda-build\meta.yaml` with the portable inventoried
`devtools/conda-build/meta.yaml`.

## How

The old shared provider `25363f2a2c902c04b2cdc8b301a3e1c1ff0c0918` uses native
relative path rendering. Its correction is owned and verified under
uibcdf/molsyssuite#112. Accepted SDK
`6d6172d6cd00c5ac2d4ebadb71df554ec5b7fa26` uses POSIX path identities;
46 focused provider controls and 447 hosted central tests pass.

Receiving source `b16b032c0d9ea177307f12991ca96d9fc6c956b8` updates the eight
`.governance-tools` checkouts and the @2 inventory, reviewing all seven changed
workflow hashes. Complete parsed workflows are equal after reversing those SDK
refs: triggers, jobs, matrices, environments, tests and publication gates are
unchanged. Independent resource/publication SDK pins stay at their existing
reviewed commits. The wrapper/provider API retains its @2 default installed
qualification and explicit declared-only candidate/native-gate route.

Its manual full matrix 37994715796 passes eight Linux/macOS cells but all four
Windows cells now fail on the exact workflow hash:

```text
Dependency routes rejected: .github/workflows/CI.yaml: reviewed workflow changed; classify its actual routes again
```

Git's `core.autocrlf=true` checkout converts LF workflow blobs into CRLF bytes.
An actual Git checkout regression reproduces that conversion and fails without
the LF attribute; `.github/workflows/* text eol=lf` preserves the reviewed
bytes. The shared digest check is not normalized or relaxed.

## Why

The administrative preflight must compare the same inventory and reviewed input
bytes on Linux, macOS arm64 and Windows. This is source CI receiving, separate
from installed artifact qualification or a new scientific implementation.

## What was refuted

- The SDK source fix alone is insufficient: native 37994715796 proves the
  next hash failure after portable discovery succeeds.
- Refreshing hashes to Windows bytes or normalizing them in the checker would
  weaken or split the exact-byte contract; preserve Git checkout bytes instead.
- Local Linux success does not establish native Windows execution.
- Neither failed matrix can become a successful executed full watermark.

## Receiving evidence and limits

Local Python 3.14.7 under `molsyssuite@uibcdf_3.14`: original adoption passes
15 declared/installed input routes, 149 owner distribution/publication/reporting
checks and one existing unresolved-report skip. The LF change passes all 13
focused distribution checks; its actual Git regression fails before the attribute
and passes after. Qualified Receptor editable imports and seven unchanged #82
workspace closure findings are retained; no shared environment is mutated.

Original receiving-head CI 37994697153, QA 37994697177, Docs 37994697155 and
policy 37994697786 pass. Policy and both QA jobs are independently identity/step
verified. Current strict PR checks and internal administrator direct pushes are
unchanged. Native Windows receiving after the LF fix is verified below.

Public 0.19.0 build 1 remains producer
`f604b940ab281df4554869fdd24f796ea6d42c27`, producer run 37520722817,
installed run 37521323117 and promotion 37522036404;
`smonitor-0.19.0-py_1.tar.bz2`, SHA-256
`4b876b4993b1e2caeed40851402a931f3b245ed7c1916d9483d81bc90274e31c`.
No rebuild, release, tag, upload, promotion or new installed-file qualification.

## Resolution

Source `57bcf31cc0508fba7f877a5eecc4ec8dd5d725bd` passes manual full
matrix [37995139887](https://github.com/uibcdf/smonitor/actions/runs/37995139887):
all twelve Linux/macOS arm64/Windows Python 3.11–3.14 cells execute successfully.
An independent native verifier binds source, workflow, event, attempt and every
required checkout/preflight/install/import/lint/test step. Complete inventory has
exactly twelve executed matrix jobs plus the schedule/probe-only detector, which
is inapplicable/skipped for this normal manual dispatch and is not counted as an
executed gate. Representative Python 3.14 jobs on each OS report 656 passed and
five ordinary skips. macOS setup/logs identify arm64.

Exact-source routine CI 37995139308, QA 37995139461 and policy 37995140043 are
independently verified for all required jobs and steps; all are successful.
Neither prior failed matrix is rewritten or counted as a passing watermark.
The source result qualifies these executed inputs, not a later candidate/public
artifact. The archival documentation change does not modify these executable,
workflow, dependency or resource inputs; its own applicable gates stay distinct.

`test_reviewed_workflow_bytes_survive_autocrlf_checkout` exercises Git's actual
CRLF conversion and fails if LF attributes disappear; the paired provider/hash
control rejects mismatched checkouts or altered workflows. Provider discovery
mechanism regression stays in uibcdf/molsyssuite#112. GH Run Receptor's local
compact report omitted the explicit rejection and retained only runner exit 1;
incoming provider feedback is uibcdf/gh-run-receptor#64, with tested local
source `f1a5901ae9543d4d79dd184e694c05b7eb2a901f`. The native fallback recovered
the diagnosis without changing its original verdict.

Central reconciliation and durable exact receipts remain
uibcdf/molsyssuite#39. Original public artifact identity, installed tests and
release ownership remain unchanged.
