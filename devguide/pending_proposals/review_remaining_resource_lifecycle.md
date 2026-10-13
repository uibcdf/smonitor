---
summary: Review remaining temporary-resource ownership and tool lifecycle
issue: uibcdf/smonitor#47
status: partial
opened: 2026-10-13
closed:
verification: inspected
area: [devtools, resources, docs, release]
guard:
normative:
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
| `freeze_project_version.py` and `build.sh` | Conda build runner owns an ephemeral copy of source until build/test/upload completes. | Writes `pyproject.toml` then `_version.py`; failure between those writes can leave a partial ephemeral tree. Existing exact-version tests cover success and invalid version, not a second-write failure. See remaining disposition below. |
| `docs/_gen_catalog.py`, `smonitor.catalog.write_catalog`, Sphinx and `devtools/devguide_index.py` | Docs task owns generated catalog pages, `_build` and queue indexes while they are useful for review. | These are maintained or ignored outputs, not disposable scratch by age. Index `--check` is read-only. The current docs build and index checks passed. No automatic cleanup is performed. |
| `devtools/sync_smonitor_guide.py` | Legacy tool targets sibling checkout files; the central registered synchronizer owns official guide delivery. | This writer has no per-target dirty/human-change guard. It was not executed on sibling clones in this review. Use the central route pending an explicit disposition below. |
| Pytest fixtures, cache and temporary output | Pytest owns `tmp_path` fixtures; caller owns requested bundles, profiling/file/JSON exports and the new identity sidecar. | Context-managed file writes close on success/failure. Existing tests cover explicit force/append behavior and the new identity export's no-overwrite default; no blanket cache or human-output deletion is authorized. |

## Remaining owner disposition

1. **Legacy guide writer:** SMonitor #47 owns deciding whether to retire the
   local writer or add explicit target ownership, clean-state and failure
   handling. Interim route: do not invoke it for synchronized guide delivery;
   use MolSysSuite's registered synchronizer. Review by 2026-11-13. Remove
   this exception once the legacy write path is retired or guarded and tested.
2. **Conda build copy:** SMonitor #47 owns a focused failure-path check for
   the two-file version freeze, or an explicit finding that runner disposal of
   a failed ephemeral copy is sufficient. Interim route: never reuse a failed
   build tree or publish its artifact; retain the runner failure log. Review
   by 2026-11-13. Close when the failure semantics are guarded or documented
   with direct hosted evidence.
3. **Historical `/tmp` attribution:** central uibcdf/molsyssuite#104 owns its
   recorded paths. The 55 paths previously inventoried there are absent, but
   their historical owner is unknown. No SMonitor source review can infer
   their owner or authorize deletion. Preserve active/human/shared resources;
   any future cleanup needs exact ownership and paths.

No primary clone, shared environment, useful build/report output, or unknown
historical resource was removed by this source review. This local report stays
`partial` until the two component dispositions are resolved. Central #104
remains independently open for suite coordination and historical attribution.
