Troubleshooting
===============

No output appears
-----------------

- Ensure `smonitor.configure()` is called.
- Check `enabled` is not set to `False`.
- Verify handlers are installed (default console handler is added on configure).

Warnings are missing
--------------------

- Set `capture_warnings=True` or `SMONITOR_CAPTURE_WARNINGS=1`.
- If `capture_logging=True`, warnings are routed through logging; use the logging handler.

Events are rejected in dev/qa
-----------------------------

- `strict_schema=True` will raise on schema errors.
- Ensure each event has `timestamp`, `level`, `message`, and `code` or `category`.
- For strict signal contracts, include the required `extra` fields.

Bundles are empty
-----------------

- Set `event_buffer_size` in `_smonitor.py` or via `smonitor.configure(...)`.
- Use `--max-events` to control how many buffered events are exported.
