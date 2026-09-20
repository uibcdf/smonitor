---
summary: Publish one staged noarch Conda artifact instead of interpreter-platform duplicates
issue: uibcdf/smonitor#16
status: resolved
opened: 2026-09-20
closed: 2026-09-20
verification: measured
area: [packaging, release, tooling]
guard: tests/test_noarch_conda_publication.py
normative:
blocked_by: []
supersedes: []
---

# Publish one staged noarch Conda artifact instead of interpreter-platform duplicates

**Reported:** 2026-09-20, after the coordinated MolSysMT--MolSysViewer staging gate
failed to solve its Linux ARM cells.

## What

SMonitor is pure Python, but its release workflow builds three interpreter jobs and asks
each action invocation to convert the result to four platform subdirectories. The public
channel therefore contains interpreter- and platform-specific copies while Linux ARM64
has no SMonitor record at all.

Publish one `noarch: python` artifact. Manual runs must name an exact commit, version, and
build number and may upload only to `staging`; only a GitHub Release may target `main`.

## How

The recipe declares `noarch: python` and the supported Python interval. The workflow
replaces its interpreter matrix with one Python 3.13 build job, validates the full
candidate SHA and local version tag before building, and uses version 2.1 of the shared
Conda action so its structured producer evidence can be retained. The repository's GH
Run Receptor rule changes from the historical composite-release workaround to the
explicit noarch Conda profile.

## Why

MolSysMT run `35499866604` measured the downstream consequence: all three Linux ARM64
cells fail dependency resolution because SMonitor and three other pure-Python support
packages have no records for that subdirectory. Repeating a pure-Python wheel for every
interpreter and native platform consumes runners without adding compatibility. One
noarch artifact covers the supported solver space and provides a reusable implementation
for `uibcdf/molsyssuite#27`.

## What was refuted

- Existing platform conversion does not provide universal coverage: Linux ARM64 is absent.
- Python-specific builds are not required by the source: SMonitor contains no compiled
  extension and its project metadata already declares the Python compatibility interval.
- A green workflow is not external publication proof. The staged coordinate will be
  checked independently in the Anaconda channel before this proposal closes.

## First hosted candidate

Run `35503093580` published exactly one `smonitor-0.15.1-py_0` record to staging and GH
Run Receptor reported one successful noarch job with structured artifact evidence.

The first external audit was invalid: although it invoked the temporary environment's
Python executable, its working directory was this source checkout, so Python placed the
checkout first on `sys.path` and imported its historical tracked `_version.py`. Repeating
the audit from `/tmp` loaded
`/tmp/smonitor-noarch-audit-py0/lib/python3.13/site-packages/smonitor/__init__.py`; both
distribution metadata and `smonitor.__version__` were exactly `0.15.1`. Build 0 was not
defective. This correction was made while the report was active rather than preserving a
false diagnosis as history.

Build 1 adds a defense even though build 0 was valid: it freezes `PKG_VERSION` into
static project metadata and `_version.py` before pip builds the package, and the recipe
test checks both installed version surfaces. Hosted run `35503447811` passed with one
noarch job and one structured evidence artifact. Clean Python 3.11 and 3.13 environments,
both invoked outside the checkout, installed `smonitor-0.15.1-py_1` and reported exact
metadata and module version `0.15.1`.

The staging channel lists additive coordinates `py_0` and `py_1`; the main `uibcdf`
channel returns no match for SMonitor 0.15.1. No release or public-channel publication
occurred.

## Acceptance criteria

- Local tests guard the noarch recipe, exact-candidate staging boundary, single-job
  topology, and structured evidence upload.
- A hosted manual run publishes exactly one staged noarch coordinate from the named SHA.
- Clean Python 3.11 and 3.13 environments install that coordinate and import SMonitor.
- Distribution metadata and `smonitor.__version__` both equal the Conda coordinate.
- No GitHub Release, tag publication, or main-channel upload is performed by the staging
  path.

## Resolution

Implemented in `1661bbd` and hardened in `8d47325`. SMonitor now builds once as a
`noarch: python` package, manual candidates are exact-SHA staging publications, GitHub
Releases are the only path to `main`, and action v2.1 producer evidence is retained for
GH Run Receptor. The repository rule declares `package_kind: noarch` rather than
inventing native-platform coverage.

Local validation passed 458 tests with 12 workers plus Ruff, formatting, devguide, and
receptor configuration gates. The hosted and registry measurements above satisfy the
acceptance criteria. The guard is `tests/test_noarch_conda_publication.py`.
