# smonitor Developer Guide — Integration Notes

## arg_digest integration
- Wrap key public entrypoints with `@signal`.
- Provide minimal argument summaries to avoid heavy serialization.
- Avoid side effects when smonitor is disabled.
- Prefer emitting structured errors with `code`, `hint`, and `context`.

## dep_digest integration
- Emit a warning when a soft dependency is missing and a guarded function is called.
- Include dependency name in `extra` for structured reporting.
- Prefer `code` identifiers for missing deps (e.g., `DEP-W001`).

## MolSysMT integration
- Replace or wrap `msm.config.setup_logging()` with `smonitor.configure()`.
- Ensure `msm.config.capture_warnings` toggles the warning bridge.
- Provide a package `_smonitor.py` with curated hints and formatting rules.
- Keep catalogs under `A/_private/smonitor/catalog.py` and metadata in `A/_private/smonitor/meta.py`.
- Use `smonitor.integrations.emit_from_catalog(...)` for consistent emission.
- Migrate `MOLSYSMT_LOG_LEVEL` / `MOLSYSMT_SIMPLE_WARNINGS` to `smonitor` profile/config.

## MolSysViewer integration
- Ensure `smonitor` is configured on import (`ensure_configured`).
- Replace direct `warnings.warn`/`logging` with catalog emission.
- Use catalog-driven messages for frontend init failures and payload diagnostics.

## Testing strategy
- Unit-test context stack push/pop under nested calls.
- Validate that warnings are captured and formatted correctly.
- Verify that unhandled exceptions emit a final error event.
- Add tests for profile formatting (`user` vs `dev` vs `qa`).
- Add tests for policy routing and rate-limiting.

## Performance considerations
- Context push/pop must be O(1).
- Avoid expensive formatting unless a handler requests it.
- Use lazy formatting in handlers (e.g., defer rich rendering).
