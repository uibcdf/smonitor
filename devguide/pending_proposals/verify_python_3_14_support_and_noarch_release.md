---
summary: Establish verified Python 3.14 support and publish a noarch release
issue: uibcdf/smonitor#17
status: active
opened: 2026-09-21
closed:
verification: measured
area: [python, packaging, ci]
guard:
normative:
blocked_by: []
supersedes: []
---

# Establish verified Python 3.14 support and publish a noarch release

**Reported:** 2026-09-21 during the dependency-ordered MolSysSuite transition in
`uibcdf/molsyssuite#29`.
**Status:** Active. Source compatibility and the complete hosted interpreter/OS matrix
are measured; staged and public artifacts and clean consumer installation remain
unverified.

## What

Extend SMonitor's declared range from Python 3.11--3.13 to 3.11--3.14 only when its own
tests, package metadata, hosted CI, published noarch artifact, and independent clean
installation agree. SMonitor is the first runtime dependency in the chain leading to
DepDigest, ArgDigest, PyUnitWizard, and Ackredit. A source checkout cannot be used as
evidence that the currently published channel artifact supports Python 3.14.

## How

First retain the feasibility measurement below. Then align `requires-python`, classifiers,
CI matrix, Conda recipe and checks, documentation, and release notes in one candidate.
Run the required suite and wheel/console checks on the supported operating systems and
interpreters. Build one exact noarch candidate in staging, install it in a clean Python
3.14 environment, and verify the installed version and origin. After every release gate
including the separate Zenodo requirement in `uibcdf/smonitor#14` passes, publish the
immutable release and verify its public artifact independently. Only then ask MolSysSuite
to mark SMonitor `admitted` and let DepDigest use its public 3.14 package.

## Why

The current `pyproject.toml` still caps Python below 3.14. The recipe in HEAD declares
`noarch: python`, but Ackredit's consumer-side observation in `uibcdf/molsyssuite#29`
reports that the published SMonitor 0.15.0 artifacts remain linux-64 interpreter-specific
builds. This channel observation has not yet been independently rechecked here. Even a
fully green source suite therefore cannot resolve a clean Python 3.14 consumer from the
current channel.

## What is measured and what is assumed

At SMonitor commit `7b10cb9db537c3ea7a531283bdebcb6624f092bc`, a temporary Linux
CPython 3.14.7 virtual environment inherited the already prepared pytest, xdist, and
pytest-receptor tools through `--system-site-packages`. NumPy 2.5.3 and Pint 0.26.1
were installed only into that temporary environment for the cross-library test. From
the SMonitor checkout:

```text
/tmp/smonitor-py314-probe.E9Hc5C/venv/bin/python -m pytest -q -n 12 --receptor=llm -p no:cacheprovider
PASS exit=0 | 461 passed, 1 skipped | 2.05s
```

The first two runs had the same 460 passing tests and one failing cross-library test:
NumPy, then Pint, was absent from the test environment. Adding those dependencies
resolved that test without a SMonitor source change. This is a source-tree feasibility
result, not a wheel-installation, Conda-resolution, macOS/Windows, or release result.

The first candidate changes `pyproject.toml` and the noarch recipe to the target range,
adds the 3.14 classifier, and extends the hosted full matrix to twelve Linux/macOS/Windows
and Python 3.11--3.14 cells. The source suite must be repeated after these changes and
the hosted run retained before the candidate can be called compatible. The routine
development CI remains on Python 3.13, as required by the central policy. The public
README badge remains on 3.11--3.13 while SMonitor is only `authorized`.

The candidate source suite was repeated in serially scheduled local runs with twelve
workers each: Python 3.14.7 passed 465 tests with two skipped, then Python 3.13 passed
the same 465 tests with two skipped. Ruff lint passed. A development wheel built from
the dirty candidate checkout had version `0.15.0+26.gb00481d.dirty`; installed outside
the checkout into the temporary Python 3.14 environment, it imported from
`site-packages`, reported `Requires-Python: <3.15,>=3.11`, and its `smonitor --help`
command succeeded. This validates a development wheel only, not a tagged or published
artifact. The CI candidate also removes the public prerelease trigger and runs Ruff's
format check alongside lint. The new MolSysSuite release-version gate remains pending
because `uibcdf/molsyssuite#32` currently requires a versioningit `tag-filter` key that
versioningit ignores; no inert key is being added here as false compliance evidence.

The first exact-commit hosted matrix, run `35580019186` on `9ec58eb`, passed eleven of
twelve cells. Windows Python 3.12 reached the test step and failed only the frame-time
bound assertion by one microsecond. The test defect was repaired in `a30438d` and
tracked to closure as `uibcdf/smonitor#18`. The exact-commit rerun `35585349618` on
`1e48f7d9b7308adb85e5d763d7e26c5da25101cd` passed all twelve cells: Linux, macOS,
and Windows on Python 3.11--3.14. The local full suite at this commit passed on Python
3.13 and 3.14 (469 passed, 3 skipped on each) with twelve workers; Ruff lint and format
checks passed. This validates source and CI compatibility, not a staged or public Conda
artifact.

## What was refuted

- The first missing-NumPy and missing-Pint failures were environmental; they did not
  demonstrate Python 3.14 incompatibility in SMonitor. The final run passed after those
  test dependencies were present.
- `noarch: python` in HEAD does not retroactively change the package already published
  on the channel. Published artifact metadata and a clean solver test are still needed.
- A green source suite is not a support claim under the central transition policy.

## Acceptance criteria

- Metadata, classifiers, CI, recipe, docs, and release notes agree on Python 3.11--3.14.
- Required local and hosted suites pass, including the cross-library test, on the
  supported interpreter/OS matrix.
- A staged exact candidate installs and works from the intended channels in a clean
  Python 3.14 environment; the public artifact passes the same independent check.
- The release is published only after its normal gates, including `uibcdf/smonitor#14`,
  pass; MolSysSuite admits SMonitor only after public distribution is verified.
- A durable local guard tests the claimed Python metadata and release workflow matrix.

## Dependencies and risks

The rollout is governed by `uibcdf/molsyssuite#29`. The release-identifier policy rollout
in `uibcdf/molsyssuite#32` currently has a reproduced inert versioningit filter and must
be corrected before it is treated as an effective release gate. None of these issues
changes the source-feasibility result above.

## Resolution

Pending package, channel, and release evidence. The hosted twelve-cell matrix is green.
