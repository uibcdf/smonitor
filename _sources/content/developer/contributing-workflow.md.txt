# Contributing Workflow

This page defines the default workflow for contributing code or documentation to SMonitor.

## 1. Start from a clean base

Use `main` as your baseline and create a focused branch for each unit of work.

Example naming:
- `docs/user-hard-vs-soft`
- `fix/lazy-registry-error-path`
- `test/decorator-when-cases`

A focused branch keeps review simple and avoids mixing unrelated concerns.

## 2. Keep commits intentional

Each commit should answer one question clearly:
- What changed?
- Why was this change needed?

Prefer several small, coherent commits over one oversized commit.

## 3. Validate locally before pushing

Minimum local checks before push:

```bash
pytest -q
```

If you touched docs:

```bash
make -C docs clean
make -C docs html
```

If you touched dependency-resolution logic, also run coverage checks (see [Testing and Coverage](testing-and-coverage.md)).

## 4. Open PRs that are easy to review

A good PR description should include:
- scope in one sentence;
- behavior changes;
- test evidence;
- documentation impact.

## 5. Preserve compatibility mindset

SMonitor is used as infrastructure in other libraries. Treat behavior changes conservatively:
- keep error messaging stable unless a change is justified;
- keep runtime resolution and lazy-loading guarantees;
- update docs when changing contracts.
