---
summary: Review remaining temporary-resource ownership and tool lifecycle
issue: uibcdf/smonitor#47
status: resolved
opened: 2026-10-13
closed: 2026-10-13
verification: reproduced
area: [devtools, resources, docs, release]
guard: tests/test_guide_sync_readonly.py::test_guide_audit_reports_drift_without_writing
normative: devguide/resource_lifecycle_review.md
blocked_by: []
supersedes: []
---

# Remaining temporary-resource and tool lifecycle review

## Scope and evidence

This is the component disposition requested by uibcdf/molsyssuite#104. The
earlier [bounded review](../resource_lifecycle_review.md) covers integration
verification (#43), operability evidence (#44), runtime file/bundle output,
selected release receipts and guide/index tools. This pass inspected the
remaining development, test, docs, build and qualification entry points on
SMonitor `main` on 2026-10-13. Source inspection is not execution on every
platform or an inventory of historical `/tmp` ownership. The 3.14 source suite
passed 712 tests with one skip during the current diagnostic work, and
`make -C docs html` completed; those executions verify task outcomes, not all
resource teardown paths.

| Operation | Owner and useful lifetime | Cleanup and current evidence |
| --- | --- | --- |
| `devtools/ci_backlog.py` | GitHub runner owns its environment; `GITHUB_OUTPUT` is an explicit runner file. Git and API children end within `subprocess.run`/`urlopen`. | Appends only the requested output fields; no task directory or deletion. Failure selects full-matrix recovery. `tests/test_ci_backlog.py` covers that route. |
| `devtools/check_distribution_inputs.py` | Caller owns optional `--output` receipt; pinned suite checkout is read-only input. | Child processes finish before return. A failed provider exits nonzero and does not write a qualifying receipt. Existing `tests/test_distribution_inputs.py` covers failure precedence, not every hosted filesystem failure. |
| `devtools/conda-build/release_route.py` and publication workflows | Release task owns exact route/public receipts and package artifacts; runner owns hosted workdirs and cache. | Explicit receipt paths are retained on success; failure leaves logs and no automatic artifact deletion. Source and existing route tests verify identity/fail-closed checks. No new release dispatch was made for this review. |
| `freeze_project_version.py` and `build.sh` | Conda build runner owns an ephemeral copy of source until build/test/upload completes. | Writes `pyproject.toml` then `_version.py`; failure between those writes can leave a partial ephemeral tree. The executed build-script failure guard now proves a nonzero freeze stops before `pip install`. The failed runner copy is not reused for publication. |
| `docs/_gen_catalog.py`, `smonitor.catalog.write_catalog`, Sphinx and `devtools/devguide_index.py` | Docs task owns generated catalog pages, `_build` and queue indexes while they are useful for review. | These are maintained or ignored outputs, not disposable scratch by age. Index `--check` is read-only. The current docs build and index checks passed. No automatic cleanup is performed. |
| `devtools/sync_smonitor_guide.py` | Legacy helper discovers sibling checkout files; the central registered synchronizer owns official guide delivery. | The helper is now read-only: it hashes source and targets, reports `in-sync`, `drift` or `missing`, and never writes. Isolated real-process tests preserve a modified sibling file. No actual sibling clone was changed in this review. |
| Pytest fixtures, cache and temporary output | Pytest owns `tmp_path` fixtures; caller owns requested bundles, profiling/file/JSON exports and the new identity sidecar. | Context-managed file writes close on success/failure. Existing tests cover explicit force/append behavior and the new identity export's no-overwrite default; no blanket cache or human-output deletion is authorized. |

## Resolution and ownership

1. **Legacy guide writer:** The local writer has been retired in place. Its
   command now only audits bytes and exits nonzero for drift/missing targets;
   MolSysSuite's registered synchronizer remains the delivery owner. The
   guard fails against the previous writer because it would overwrite the
   fixture's human-modified guide. The README and developer checkpoint now
   describe this read-only role.
2. **Conda build copy:** The two writes are confined to the Conda build runner's
   ephemeral source copy. A simulated freezer failure executed through the
   actual `build.sh` exits 7 and never invokes `pip install`; the workflow
   cannot proceed to a successful build/upload from that copy. The runner
   owns disposal of the failed copy, while the release task retains the
   failure log. This is sufficient for the component's source lifecycle
   disposition; no atomic two-file claim or hosted teardown proof is made.
3. **Historical `/tmp` attribution:** central uibcdf/molsyssuite#104 owns its
   recorded paths. The 55 paths previously inventoried there are absent, but
   their historical owner is unknown. No SMonitor source review can infer
   their owner or authorize deletion. Preserve active/human/shared resources;
   any future cleanup needs exact ownership and paths.

No primary clone, shared environment, useful build/report output, or unknown
historical resource was removed by this source review. The source review and
two focused executed guards close the local #47 disposition. Central #104
remains independently open for suite coordination and historical attribution.
