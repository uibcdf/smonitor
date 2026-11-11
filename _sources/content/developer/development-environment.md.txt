# Development Environment

This page gives you a practical setup loop for productive development.

## 1. Install local dependencies

Use the project environment and install development requirements according to this repository's tooling.

## 2. Quick verification loop

Run this loop frequently while developing:

```bash
pytest -q
```

For docs work:

```bash
make -C docs html
```

## 3. Coverage loop

When changing logic, run coverage in addition to unit tests:

```bash
pytest --cov=smonitor --cov-report=term-missing
```

Coverage numbers are not a target by themselves; they are a proxy for missing behavior tests.

## 4. What to watch during docs builds

Current toolchain can emit repeated `RemovedInSphinx10Warning` warnings from `myst_nb`. These come from upstream compatibility and are not necessarily content issues.

Still treat these as blocking:
- broken references;
- missing documents in toctrees;
- malformed directives.
