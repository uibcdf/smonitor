# Production Checklist

Use this checklist before releasing a library integrated with SMonitor.

## Integration contract

- [ ] `_smonitor.py` exists in package root.
- [ ] `A/_private/smonitor/catalog.py` defines all active warning/error codes.
- [ ] `A/_private/smonitor/meta.py` provides docs/issues URLs.
- [ ] `A/_private/smonitor/emitter.py` uses `DiagnosticBundle`.
- [ ] package `__init__.py` calls `ensure_configured(PACKAGE_ROOT)`.

## Message quality

- [ ] user-facing messages are explicit and actionable.
- [ ] hints explain how to fix or avoid the issue.
- [ ] no hardcoded warning/error strings bypass catalog.
- [ ] profile-specific behavior (`user`, `dev`, `qa`, `agent`) is verified.

## Instrumentation and contracts

- [ ] major public entry points are decorated with `@signal`.
- [ ] exploratory probes use appropriate exception level (`DEBUG` when expected).
- [ ] `SIGNALS` contracts are defined for critical paths.
- [ ] strict-signal QA test passes.

## Reliability

- [ ] emission fallback paths are not silently swallowed.
- [ ] handler failure does not break core functionality.
- [ ] bundle export works with representative runs.

## CI and release

- [ ] tests pass (`pytest -q`).
- [ ] docs build passes (`make -C docs html`).
- [ ] CLI smoke checks pass.
- [ ] release notes mention diagnostics-impacting changes.

If all items are checked, your integration is generally ready for production release.
