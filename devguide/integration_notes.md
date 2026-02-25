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
- Keep catalogs under `molsysmt/_private/smonitor/catalog.py` and metadata in `molsysmt/_private/smonitor/meta.py`.
- **Recommendation**: Use `smonitor.integrations.DiagnosticBundle` to centralize `warn` and `resolve` helpers.
- **Recommendation**: Inherit from `CatalogException` and `CatalogWarning` for all diagnostic classes.
- Migrate `MOLSYSMT_LOG_LEVEL` / `MOLSYSMT_SIMPLE_WARNINGS` to `smonitor` profile/config.

## MolSysViewer integration
- Ensure `smonitor` is configured on import (`ensure_configured`).
- Replace direct `warnings.warn`/`logging` with catalog emission via `DiagnosticBundle`.
- Use catalog-driven messages for frontend init failures and payload diagnostics.

## Testing strategy
- Unit-test context stack push/pop under nested calls.
- Validate that warnings are captured and formatted correctly.
- Verify that unhandled exceptions emit a final error event.
- Use `Manager.resolve()` to test message interpolation without side effects.
- Add tests for profile formatting (`user` vs `dev` vs `qa`).
- Add tests for policy routing and rate-limiting.
- Add tests for probing contracts: expected probe misses must be `DEBUG` and
  must not leak as `ERROR` in `user` profile.

## Performance considerations
- Context push/pop must be O(1).
- Avoid expensive formatting unless a handler requests it.
- Use lazy formatting in handlers (e.g., defer rich rendering).

## Open Architectural Questions

### Manager-Catalog Integration
How should `Manager.emit()` interact with external Catalogs?
- **Decision**: Hybrid Approach. 
    1.  `Manager.emit()` handles profile-based resolution if `CODES` are injected at config time.
    2.  Integration helpers (`DiagnosticBundle`, `CatalogException`) resolve messages using `Manager.resolve()` to allow pre-flight formatting (essential for Exception messages).
    3.  This ensures clean code in the libraries while keeping `smonitor` as the single source of truth for profile logic.

## Probing Contract (Cross-Library)
For integrations with `molsysmt`, `pyunitwizard`, `argdigest`, and `depdigest`:

- Non-matching exploratory probes are expected and should be classified as
  `DEBUG`.
- `WARNING` and `ERROR` should be reserved for actionable anomalies and true
  operation failures.
- Prefer explicit codes/tags (for example `PUW-DBG-PROBE-001`) to make QA
  triage deterministic.

## Recent hardening decisions

- `DiagnosticBundle.warn` no longer silently swallows emission failures; it now
  emits a fallback integration diagnostic and preserves plain `warnings.warn`.
- `@signal` exception emission uses function-granular `source` (`module.func`),
  while SIGNALS contracts keep module-prefix compatibility fallback.
- `SMONITOR_PROFILING_SAMPLE` env parsing is now safe (invalid/out-of-range
  values are ignored).
- `reset_configured_packages()` is available in `smonitor.integrations` for
  test/dynamic sessions.
- `CatalogException` and `CatalogWarning` now support both nested and flat
  catalog shapes.
- Manager reports now include `handler_errors_total`, `degraded_handlers`, and
  `runtime_warnings`; optional threshold warning via
  `handler_error_threshold`.
