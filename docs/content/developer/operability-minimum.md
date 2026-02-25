# Operability Minimum

This page defines the minimum operational loop for small teams maintaining
SMonitor-integrated libraries.

## Weekly checks (recommended)

1. Top repeated warning/error codes.
2. New unknown or uncatalogued codes.
3. Error trend by library and version.
4. Bundle quality in incoming support reports.

## Release-candidate checks

- `pytest` in clean environment.
- `make -C docs html` without broken references.
- API contract tests pass.
- one integration smoke run in each ecosystem library.

## Support loop

1. Reproduce from message + minimal script.
2. If needed, reproduce from diagnostics bundle.
3. Triage by `code` and `trace_hash`.
4. Patch with tests.
5. Publish changelog entry referencing affected codes.

## What to automate first

- contract checks (`strict_signals`, `strict_schema`);
- bundle export smoke step in CI;
- docs build gate;
- issue templates that request code/reproducer/environment.

## AI-assisted loop (optional)

- use `agent` profile and structured bundles for triage;
- keep human review mandatory for all proposed fixes;
- store triage decisions for recurring patterns.

## Why this matters

For small teams, predictable operational loops reduce support cost more than
ad-hoc debugging sessions, and keep diagnostics quality stable over time.
