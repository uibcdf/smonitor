# Troubleshooting

Use this page as a fast diagnosis map.

## Symptom: no diagnostics are visible

Check:
1. `ensure_configured(PACKAGE_ROOT)` is called on import.
2. `_smonitor.py` exists in package root with exact name.
3. handlers are active (`smonitor.report()` and manager state).

## Symptom: warning message has no template/hint

Check:
1. emitted `code` exists in active catalog,
2. message fields (`user_message`, `dev_message`, etc.) exist,
3. placeholders required by template are in `extra`.

## Symptom: strict signals fail in QA

Check:
1. signal source matches the expected contract key,
2. all `extra_required` fields are present,
3. test profile enables the intended strict mode.

## Symptom: duplicate messages

Check:
1. custom logging handlers are not re-emitting same event,
2. warnings capture and logging capture are not duplicated manually.

## Symptom: bundle has no events

Check:
1. `event_buffer_size` is greater than 0,
2. events are emitted after configuration,
3. export command points to the same runtime context.

## Symptom: users see overly technical output

Check:
1. default profile in `_smonitor.py` is `user`,
2. dev/debug overrides are not leaking into user runtime.

## If still blocked

Prepare a minimal reproducer with:
- package `_smonitor.py`,
- one decorated function,
- one catalog code,
- one failing call.

Then compare against:
- [SMONITOR_GUIDE.md](https://github.com/uibcdf/smonitor/blob/main/standards/SMONITOR_GUIDE.md)
- [Mini Library Walkthrough](mini-library-walkthrough.md)
