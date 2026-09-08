---
summary: Publish the 0.14 profile-message fallback for downstream CI
issue: uibcdf/smonitor#8
status: resolved
opened: 2026-09-07
closed: 2026-09-08
verification: measured
area: [release, integration]
guard:
normative: CHANGELOG.md
blocked_by: []
supersedes: []
---

# Publish the 0.14 profile-message fallback for downstream CI

## What

The profile-message fallback existed on SMonitor main and in immutable tag `0.14.0`, but
MolSysSuite consumers resolving SMonitor from the UIBCDF Conda channel still received
0.13.0. PyUnitWizard consequently could not require the corrected behavior in CI; its
consumer residue is tracked in `uibcdf/pyunitwizard#71`.

## How

Publish the existing immutable tag as a GitHub Release and build the Conda distributions
used by downstream Python 3.11, 3.12, and 3.13 environments. Treat GitHub workflow state
and external registry state as separate evidence. The tag is not moved and no later main
commit is retroactively included in 0.14.0.

## Why

Before 0.14.0, a catalog entry defining only `user_message` renders empty under machine
profiles such as `qa` and `agent`. PyUnitWizard uses that supported catalog shape, so its
CI needs a distributed provider version before it can raise the dependency floor and
guard the behavior.

## What is measured and what is assumed

- GitHub Release `0.14.0` was published on 2026-09-08 for commit
  `59bf831cd21cb0608e6f56a3f6d00135f35e2951`.
- GitHub Actions run `34278594890` completed with conclusion `success` and three successful
  Python-matrix jobs.
- GH Run Receptor 0.19.0 selected the repository's `release` profile, returned `PASS`, and
  retained the exact event, ref, and SHA while reporting `registry=not_observed`.
- The public Anaconda release API independently returned 12 SMonitor 0.14.0 distributions:
  Python 3.11--3.13 on `linux-64`, `osx-64`, `osx-arm64`, and `win-64`, all on label
  `main`.
- PyPI returned 404 for the `smonitor` project at verification time. This release therefore
  claims the supported UIBCDF Conda and GitHub source paths, not PyPI publication.

## What was refuted

- A successful Actions run alone was not accepted as proof of registry delivery; Anaconda
  was queried independently.
- The original Conda receptor rule could not observe platforms built inside the composite
  action. That integration was corrected in `uibcdf/smonitor#10`, while structured
  provider work remains in `uibcdf/gh-run-receptor#35`.
- Moving tag `0.14.0` to include later SMonitor work was rejected because release tags are
  immutable.

## Scope and exclusions

This publication does not include the later derived `.hint` property on SMonitor main,
does not publish to PyPI, and does not make GH Run Receptor the sole release authority.

## Acceptance criteria

- The GitHub Release exists and names immutable tag `0.14.0`.
- Conda exposes all 12 supported Python/platform distributions on label `main`.
- Public status documentation no longer describes 0.14.0 as unpublished.
- Downstream consumers can resolve the release before closing their own blocked work.

## Resolution

The GitHub source release and all expected Conda distributions are public. The changelog
is the durable release record, the README identifies 0.14.0 as current, and downstream
dependency-floor validation can proceed independently.
