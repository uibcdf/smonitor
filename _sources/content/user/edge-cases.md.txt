# Edge Cases

This page covers integration situations that usually cause regressions.

## 1. Exploratory probes produce noisy errors

Problem:
- helper functions that intentionally test many formats raise frequent exceptions.

Fix:
- mark those with `@signal(exception_level="DEBUG")`,
- keep assertive parsing paths at `ERROR`.

An inner signal whose event is filtered does not consume the exception's
diagnostic observation. An eligible enclosing signal can still record that
failure. Once a signal accepts an observation, enclosing signals avoid duplicate
events; an accepted DEBUG observation is not promoted to ERROR by an outer
wrapper. Application enablement, source silence and the current level threshold
control acceptance. Coalescing and duplicate policies retain their own behavior.

## 2. Duplicate warnings through logging bridge

Problem:
- warning appears twice when logging/warnings interception is misconfigured.

Fix:
- rely on SMonitor capture policy,
- avoid custom parallel warning bridges unless required.

## 3. Contract mismatch between SIGNALS and emitted extra

Problem:
- `SIGNALS` requires fields that emitters do not pass.

Fix:
- in QA, enable `strict_signals=True`,
- add targeted tests for each critical signal.

## 4. Silent emission failure

Problem:
- emission errors are swallowed and observability disappears.

Fix:
- never use `except Exception: pass` in diagnostics paths,
- provide explicit fallback warning/log line with context.

## 5. Over-instrumentation

Problem:
- adding `@signal` everywhere increases overhead and noise.

Fix:
- instrument API boundaries and orchestration,
- skip tight loops and low-level utility hot paths.

## 6. Conflicting runtime configuration

Problem:
- tests, notebooks, and scripts override profile differently.

Fix:
- be explicit in each execution context,
- remember precedence: runtime > env > `_smonitor.py`.

## Next

Continue with [Troubleshooting](troubleshooting.md).
