# Reading Messages in Library A

When library `A` uses SMonitor, warnings and errors are designed to be actionable.

These messages are guidance, not blame. Their goal is to help you complete your
task with fewer retries.

## Typical message structure

- what happened,
- where it happened (`source` or function context),
- how to fix it (`hint`),
- optional code ID (for support and tracking).

Depending on how library `A` is configured, you may see:
- plain text output, or
- richer visual cards (same diagnostic meaning, different presentation).

## Quick interpretation table

| What you see | What it usually means | What to do |
|---|---|---|
| `WARNING` | Operation can often continue, but something is suboptimal or ambiguous. | Apply hint if available, then continue. |
| `ERROR` | Operation failed for current input or state. | Apply hint/fix input and retry. If still failing, report with code/message. |

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

## Before/after quality example

Less helpful:

```text
ValueError: invalid argument
```

More helpful:

```text
ERROR [MYLIB-E101]: Argument 'selection' has invalid format: all_atoms.
Hint: Use a selector like atom_name == 'CA' or chain_id == 'A'.
```

The second message reduces guesswork and gives you a direct next action.
