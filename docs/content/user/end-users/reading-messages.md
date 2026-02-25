# Reading Messages in Library A

When library `A` uses SMonitor, warnings and errors are designed to be actionable.

## Typical message structure

- what happened,
- where it happened (`source` or function context),
- how to fix it (`hint`),
- optional code ID (for support and tracking).

Depending on how library `A` is configured, you may see:
- plain text output, or
- richer visual cards (same diagnostic meaning, different presentation).

## How to use a message effectively

1. Read the message text first (problem summary).
2. Apply the suggested hint.
3. If it persists, keep the exact message/code for support.

## Example

```text
WARNING [MYLIB-W001]: Selection 'all' may be too broad.
Hint: Use a more specific selector, for example atom_name == 'CA'.
```

This message already tells you:
- the likely issue,
- a concrete correction,
- the code to mention if you open a report.
