# Conda release routes for SMonitor

SMonitor publishes one `noarch: python` Conda artifact. This is a local implementation
pilot for the two-route contract proposed in `uibcdf/molsyssuite#27`, not a universal
workflow for native or multi-artifact packages. The normal, unstaged route remains a
stable GitHub Release; staging is required only when its pre-public evidence is needed.

## Decide before the tag

For every new version, the release maintainer completes and reviews
`devtools/conda-build/release_plan.toml` **in the candidate commit**. Its deliberately
empty template is not releasable. Set the three-part `version`, `route` (`direct` or
`staged`), a specific `reason`, `decision_by`, and every required workflow path. Keep
`.github/workflows/CI_full_matrix.yaml` in `required_workflows`. Do not record a run ID
or candidate SHA in the committed plan: the workflow binds the final commit SHA to
successful exact-commit run IDs in its retained receipt. Run the full matrix manually
on the final candidate commit before publishing. If that commit changes, rerun it.

Choose `staged` if an installed candidate must pass a gate before public visibility,
Python/platform coverage, packaging or dependency resolution has changed materially,
or any artifact for the version already exists in an Anaconda label. A coupled
consumer or ambiguous registry state also requires staging or a pause. Choose `direct`
only if none of those conditions applies, dependencies resolve from public channels,
the normal CI and release gates have passed, and the action can test the package before
its first upload. A package being noarch or a patch release is not sufficient evidence
by itself. Record the applicable reasoning in the plan; the complete shared criteria
remain under review in `uibcdf/molsyssuite#27`.

## Direct route: routine independent release

After the exact-commit gates pass, create the immutable `X.Y.Z` tag and publish its
stable GitHub Release. The release event invokes
`.github/workflows/build_and_upload_conda_packages.yaml`. Before Conda setup or any
upload, it verifies the committed `direct` decision, tag/commit identity, successful
full-matrix run at that SHA, and an explicit Anaconda 404 for the entire version.
Registry errors and any existing distribution fail closed. The action then builds and
tests build `py_0` from public dependencies, uploads it once to `main`, retains its
producer evidence, and independently compares the public record with the built file's
SHA-256. It does not use `--force`.

The GitHub Release becomes public before the Conda job finishes. A failed job means
the release is incomplete: investigate and report it; do not describe Conda as
published or simply rerun a possibly occupied upload. The central proposal must still
decide whether this bounded non-atomic interval remains acceptable.

## Staged route: installed-candidate evidence first

Commit `route = "staged"` before candidate work. Manually dispatch the same build
workflow with the full `candidate_sha`, exact `version`, and non-negative
`build_number`. It checks the candidate and its full-matrix run, then builds and tests
only to `uibcdf/label/staging`. An existing version tag must match that SHA; otherwise
only a runner-local tag is created for version derivation. A defective candidate gets
a higher build number, never overwritten bytes.

Independently verify the exact staged coordinate, SHA-256, installed-candidate gates,
and any coupled consumers. Only then tag the *same* SHA and publish its stable GitHub
Release. Its release-event job validates the staged plan and exact-commit gates, then
skips the direct uploader and installed-package smoke job. Dispatch
`.github/workflows/promote_conda_package.yaml` with the exact tag SHA, version, build
number and verified digest. It checks the published release and exact-commit gates,
then uses the shared `promote@v2.2.2` action to add the `main` label to the **same file**.
The staging label is retained. The promotion receipt and an independent public query
provide poststate evidence. Do not rebuild, re-upload, choose the newest staging build
implicitly, or move the tag.

## Evidence and scope

Retain the route receipt, producer or promotion evidence, complete workflow conclusion,
and independent Conda query with the exact file and SHA-256. GH Run Receptor provides a
compact first inspection, but its summary does not replace those primary checks.
The 0.16.0 and 0.17.0 exact-file promotions are proven in hosted runs; the guarded
direct route has local contract tests but has **not** yet been exercised by a new
public release. The 0.17.0 release event incorrectly reported a failed direct
workflow despite successful staged promotion; `uibcdf/smonitor#28` tracks the
corrected routing and its first hosted proof.
Track that first live proof in `uibcdf/smonitor#20`. Native ABI3 publishers should
reuse the decision and evidence contract, not copy this one-job noarch build shape.
