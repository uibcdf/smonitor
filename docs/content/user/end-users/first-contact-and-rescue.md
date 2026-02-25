# First Contact and Rescue for End Users of Library A with Embedded SMonitor

You do not need to learn SMonitor internals to use library `A` successfully.

Treat these messages as in-product guidance to help you finish tasks with less
trial and error.

## First contact

When `A` shows a diagnostic:
- read the first line (`WARNING` or `ERROR`),
- read the hint,
- apply the suggested correction.

## Rescue flow (30 seconds)

1. Read message and hint.
2. Apply fix.
3. Retry once.

If it still fails:
1. keep full message text and code ID,
2. capture a minimal reproducer,
3. share version/environment info,
4. optionally provide a redacted diagnostics bundle.

## Interpretation rule

- `WARNING`: operation often continues; review quality/ambiguity.
- `ERROR`: operation failed; input/state likely needs correction.

## Important note

SMonitor diagnostics are meant to assist, not punish. They are designed to
reduce confusion and speed up resolution.
