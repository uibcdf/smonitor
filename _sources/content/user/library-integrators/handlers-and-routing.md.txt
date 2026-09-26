# Handlers and Routing Patterns

This page gives practical guidance for choosing handlers and routing events in
a host library.

## Handler roles

- `console`: interactive diagnostics for users and developers.
- `file`: durable plain-text logs for local debugging.
- `json`: machine-readable stream for QA pipelines and tooling.
- `memory`: in-process buffer used for exports and support bundles.

## Minimal production baseline

For most libraries:
- `console` for user-facing feedback,
- `json` for QA/automation pipelines,
- `memory` enabled when bundle export is part of support workflow.

## Example configuration

```python
SMONITOR = {
    "handlers": ["console", "json"],
    "event_buffer_size": 500,
}

ROUTES = [
    {"when": {"level": "ERROR"}, "send_to": ["console", "json"]},
    {"when": {"level": "WARNING"}, "send_to": ["console"]},
]

FILTERS = [
    {"when": {"code": "MYLIB-W001"}, "rate_limit": "1/100@60"},
]
```

## Routing principles

1. Keep `ERROR` events in both human and machine channels.
2. Apply rate limits only to repetitive non-critical warnings.
3. Avoid dropping events that are part of published contracts.
4. Keep routing deterministic so CI and local runs are comparable.

## Failure behavior

If one handler fails, SMonitor should still attempt delivery to remaining
handlers. Validate this in QA with a degraded-handler test case.

## Validation checklist

- representative warnings appear once in console;
- machine stream receives expected `code` and `signal`;
- bundle export includes expected recent events;
- repetitive noise is reduced by policy, not by deleting diagnostics.
