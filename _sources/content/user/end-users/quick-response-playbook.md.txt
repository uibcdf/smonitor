# Quick Response Playbook

Use this when a warning or error appears and you want to continue with minimal
friction.

## 30-second flow

1. Read the first line: identify `WARNING` or `ERROR`.
2. Apply the suggested hint (if present).
3. Retry the same operation once.

## If it still fails

1. Keep the message text and code ID (for example `MYLIB-W001`).
2. Copy a minimal reproducer (small script or notebook cell).
3. Share those with the maintainers of the host library.

## Rule of thumb

- `WARNING`: operation often continues, but result quality may be affected.
- `ERROR`: operation failed; apply hint or report with reproducible context.

You do not need to understand SMonitor internals to use this workflow.

## When it is usually safe to continue after a warning

You can often continue if:
- output is still produced,
- warning indicates ambiguity or a non-critical fallback,
- results look consistent with your expectation.

Stop and inspect if:
- warning repeats many times unexpectedly,
- warning appears near critical publication/production steps,
- output quality is uncertain.
