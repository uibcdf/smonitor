# AGENTS

## External Tooling Guides (Required for Development)

These guides are required reading for anyone developing this library. They describe how external tools must be used here.

- `standards/SMONITOR_GUIDE.md` — Required guide for SMonitor integration and diagnostics.

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
