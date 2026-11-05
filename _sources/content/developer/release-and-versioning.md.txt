# Release and Versioning

This page summarizes the practical release flow used in this repository.

## Pre-1.0 Stabilization Window

Stabilization window started on **2026-02-27**.

During this period:
- only bugfix/hardening/docs/test changes are accepted by default;
- each PR must pass the stabilization gates:
  - `pytest`
  - docs build (`make -C docs html`)
  - QA smoke (build/install/CLI)
- diagnostics contract changes (`code`, `signal`, payload fields) must be explicitly documented.

## 1. Prepare release content

SMonitor declares the unchanged MIT license through SPDX metadata and includes
the exact repository `LICENSE` notice. Setuptools >=77.0.3 is required for
these fields, including Conda host and no-build-isolation routes. After building
artifacts, run `python devtools/check_license_artifacts.py`; this checks notice
bytes and metadata in the wheel and sdist, then builds and checks a new wheel
from that sdist. This local administrative check does not qualify a release or
replace installed-package/publication gates.

Before tagging:
- ensure tests pass;
- ensure docs build;
- ensure README and docs reflect actual behavior;
- verify ignored/generated files are not accidentally tracked.

## 2. Commit and push release-ready state

Create coherent commits and push `main`.

## 3. Create and push tag

Use semantic version tags (for example `0.2.0`) when release scope is clear and repository state is stable.

## 4. Post-tag validation

After pushing a tag:
- verify release badge/version links;
- verify docs references to release when applicable;
- confirm no local drift remains.
