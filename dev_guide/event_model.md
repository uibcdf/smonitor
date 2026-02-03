# smonitor Developer Guide — Event Model

## Event Schema
Each emitted event is a dictionary with the following keys:

- `timestamp`: ISO 8601 string.
- `level`: one of `DEBUG`, `INFO`, `WARNING`, `ERROR`.
- `source`: library/module (e.g., `molsysmt.select`).
- `message`: human-readable message.
- `context`: breadcrumb stack and metadata.
- `extra`: optional structured data.

Example:
```json
{
  "timestamp": "2026-02-03T12:00:00Z",
  "level": "WARNING",
  "source": "molsysmt.select",
  "message": "Selection string is ambiguous",
  "context": {
    "chain": ["molsysmt.view", "arg_digest", "molsysmt.select"],
    "depth": 3
  },
  "extra": {
    "selection": "atom_name==CA"
  }
}
```

## Context Structure
The `context` section is produced by `core.context` and contains:
- `chain`: ordered list of frames
- `depth`: number of frames included
- `frames`: optional detailed frame data

Example frame:
```json
{
  "function": "select",
  "module": "molsysmt.basic",
  "args": {"selection": "atom_name==CA"},
  "time": "2026-02-03T12:00:00Z"
}
```

## Handler Contract
Handlers receive the full event dict and must:
- be side-effect safe
- avoid raising exceptions (errors should be swallowed or logged)
- support a minimal `handle(event)` interface

## Severity Routing
- The manager filters by `level` before dispatching.
- Handlers can implement additional filtering.

## Backward Compatibility
- If context data is not available, `context` may be `None`.
- Handlers should not assume `extra` exists.
