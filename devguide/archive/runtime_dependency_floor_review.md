---
summary: Adopt reviewed minimum-only optional runtime provider requirements.
issue: uibcdf/smonitor#55
status: resolved
opened: 2026-11-04
closed: 2026-11-04
verification: measured
area: [maintenance, contracts]
guard: tests/test_rich_provider_contract.py
normative:
blocked_by: []
supersedes: []
---

# Runtime dependency floor review

Review completed against pyproject.toml, the sole Conda recipe, all five
maintained environment routes, resources.toml, dependency_routes.toml and
active CI/publication workflows. Required runtime providers remain empty.
Optional rich>=13 consumes Console/Theme/Text/Panel/Rule/Table; pytest>=8
provides plugin hooks; pytest-receptor>=1.2 provides extension and artifact APIs.

No concrete incompatibility justified pytest<10 or receptor<2; those product
ceilings are removed and maintained usage guidance agrees. Python's separately
governed range and reproducibility-only tool pins/bounds remain. No optional
feature becomes mandatory. The schema reader still rejects incompatible schemas.

Minimum cohort qualification used a disposable Python 3.12 environment with
pytest 8.0.0, receptor 1.2.0, Rich 13.0.0 and xdist 3.6.1: 16 existing bridge/
policy/console checks and four real Rich profile controls passed. Routine
Python 3.14 uses pytest 9.1.1, Rich 15.0.0 and the installed receptor 1.2 source
generation. This does not certify future versions or every interpreter matrix.
The maintained dependency-contracts guide records APIs, floors and boundaries.

The shared caller environment's pip check reports unrelated missing pdb2pqr and
NumPy/BioPython restrictions in packmol-memgen/proprep/ndfes/fetkutils/edgembar.
No caller environment was changed to repair those findings; compatibility
qualification was isolated. Central receiving belongs to uibcdf/molsyssuite#137;
the workspace finding belongs to its existing #82 coordination.

## Final guidance correction, 2026-11-04

The canonical guide's introductory Receptor requirement still repeated the
removed <2 ceiling after the Conda example was corrected. Both now state >=1.2.
A separate Python 3.14 isolated control with public pytest-receptor 1.2.2,
pytest 9.1.1 and Rich 15.0.0 passes twelve bridge/policy/real-Rich tests.
