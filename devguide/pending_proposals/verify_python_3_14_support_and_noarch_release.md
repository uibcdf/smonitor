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
**Status:** Active. Source compatibility is measured on Linux; packaging, hosted
platforms, public artifacts, and clean consumer installation remain unverified.

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

Pending hosted, package, channel, and release evidence.
