# Contributor Checklist

Use this checklist before opening a PR or creating a release commit.

## Code and behavior

- [ ] Soft dependencies are not imported at module top level.
- [ ] Dependency checks happen at runtime where expected.
- [ ] Error/warning messages stay actionable and consistent.

## Diagnostics

- [ ] SMonitor changes follow `SMONITOR_GUIDE.md`.
- [ ] No hardcoded diagnostic strings bypassing the catalog.
- [ ] Emission failure paths preserve fallback context.
- [ ] `SMONITOR_GUIDE.md` needs updates?

## Tests and coverage

- [ ] `pytest -q` passes.
- [ ] Coverage command run for behavioral changes.
- [ ] New behavior has explicit tests.

## Documentation

- [ ] User docs updated for integration-facing changes.
- [ ] Developers docs updated for contributor-facing changes.
- [ ] Contract links point to canonical sources (`main` branch URLs when remote links are needed).
- [ ] `make -C docs html` succeeds.

## Git hygiene

- [ ] Commits are focused and well named.
- [ ] No generated artifacts accidentally tracked.
- [ ] Branch is ready for review or release tagging.
