---
summary: Publish one staged noarch Conda artifact instead of interpreter-platform duplicates
issue: uibcdf/smonitor#16
status: active
opened: 2026-09-20
closed:
verification: measured
area: [packaging, release, tooling]
guard:
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
Run Receptor reported one successful noarch job with structured artifact evidence. The
independent clean-environment audit rejected that artifact: under both Python 3.11 and
3.13, `importlib.metadata.version("smonitor")` returned `0.13.0+9.g0ec2ef9`, not the
Conda coordinate `0.15.1`.

The source copy used by conda-build cannot derive the candidate tag and falls back to the
tracked `_version.py`. The corrective path therefore freezes `PKG_VERSION` into static
project metadata and `_version.py` before pip builds the package, and the recipe test
checks both installed version surfaces. Build 0 remains rejected evidence; it is not
overwritten. The correction will use additive build 1.

## Acceptance criteria

- Local tests guard the noarch recipe, exact-candidate staging boundary, single-job
  topology, and structured evidence upload.
- A hosted manual run publishes exactly one staged noarch coordinate from the named SHA.
- Clean Python 3.11 and 3.13 environments install that coordinate and import SMonitor.
- Distribution metadata and `smonitor.__version__` both equal the Conda coordinate.
- No GitHub Release, tag publication, or main-channel upload is performed by the staging
  path.
