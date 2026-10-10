# AGENTS

## External Tooling Guides (Required for Development)

These guides are required reading for anyone developing this library. They describe how external tools must be used here.

- `standards/SMONITOR_GUIDE.md` — Required guide for SMonitor integration and diagnostics.
- `GH_RUN_RECEPTOR_GUIDE.md` — Required guide for compact, truth-preserving inspection of
  GitHub Actions runs and the native-command fallback.
- `PYTEST_RECEPTOR_GUIDE.md` — Required guide for compact, truth-preserving pytest output
  in local and hosted development.
- `MOLSYSSUITE_GUIDE.md` — Required suite-governance guide owned by
  `uibcdf/molsyssuite`; this synchronized copy must not be edited locally.

## SMonitor Agent Contract (Required)

If you are an automation agent contributing to this repository:

1. Use catalog-driven diagnostics only.
- Do not hardcode user-facing warning/error strings in library logic.

2. Preserve stable contracts.
- Keep `code` and `signal` semantics stable once published.

3. Respect profile intent.
- Keep `agent` outputs compact and machine-readable.
- Keep `user` outputs explicit and actionable.

4. Validate before proposing changes.
- Run tests relevant to modified modules.
- Preserve API contract tests and integration contract tests.

5. Keep support reproducibility intact.
- Do not break bundle export flows.
- Maintain redaction-safe defaults for shared diagnostics artifacts.

## Modular reusable tools

Before adding a feature, inspect existing tools and identify the owning module or
component. Implement or extend independently useful operations as documented reusable
tools in that owner, with their own contracts and tests; have consumers call them.
Keep task-specific decisions local and report missing sibling capabilities to the
provider with linked consumer evidence. Follow
[MOLSYSSUITE_GUIDE.md#modular-reusable-tools](MOLSYSSUITE_GUIDE.md#modular-reusable-tools)
for applicability, compatibility, performance and tracked exceptions.

## Durable working instructions

Keep technical findings in owning issues, fixes, tests and maintained guidance.
Place only accepted lasting contributor actions in root or appropriately scoped
instructions, following
[the common policy](MOLSYSSUITE_GUIDE.md#durable-working-instructions).
For work under `devguide/`, also read [devguide/AGENTS.md](devguide/AGENTS.md)
and its local reporting protocol. Shared instruction proposals belong in
`uibcdf/molsyssuite`; cross-MOLI contracts belong in `uibcdf/moli`.

## Human-facing issue feedback

Surface actionable suspected defects, inconsistencies, missing analyses and
improvements, including uncertain or nonblocking findings. When working with a
human, offer an owning issue at a natural pause; retain existing reporting
authorization and respect declined/deferred disclosure. Follow
[the accepted feedback route](MOLSYSSUITE_GUIDE.md#human-facing-issue-feedback)
for ownership, uncertainty, privacy and exceptions.
