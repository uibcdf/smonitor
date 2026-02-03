# smonitor Developer Guide — Integration Notes

## arg_digest integration
- Wrap key public entrypoints with `@signal`.
- Provide minimal argument summaries to avoid heavy serialization.
- Avoid side effects when smonitor is disabled.

## dep_digest integration
- Emit a warning when a soft dependency is missing and a guarded function is called.
- Include dependency name in `extra` for structured reporting.

## MolSysMT integration
- Replace or wrap `msm.config.setup_logging()` with `smonitor.configure()`.
- Ensure `msm.config.capture_warnings` toggles the warning bridge.
- Provide a project `_monitor.py` with curated hints and formatting rules.

## Testing strategy
- Unit-test context stack push/pop under nested calls.
- Validate that warnings are captured and formatted correctly.
- Verify that unhandled exceptions emit a final error event.

## Performance considerations
- Context push/pop must be O(1).
- Avoid expensive formatting unless a handler requests it.
- Use lazy formatting in handlers (e.g., defer rich rendering).
