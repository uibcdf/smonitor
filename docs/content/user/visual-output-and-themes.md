# Visual Output and Themes

SMonitor supports two main console styles:
- `theme="plain"` (default, minimal dependencies),
- `theme="rich"` (enhanced visual cards and structured blocks).

## Why this matters

Good diagnostics are not only correct. They must also be easy to scan quickly
under pressure (debugging, QA, support sessions).

## Enabling rich output

Install the optional dependency:

```bash
python -m pip install rich
```

Configure your library profile:

```python
import smonitor

smonitor.configure(profile="user", theme="rich")
```

If `rich` is not available, SMonitor falls back to plain console output.

## Profile behavior

- `user`: concise message + hint focus.
- `dev`/`debug`: more technical blocks with source/context details.
- `qa`: structured summary for reproducibility.
- `agent`: machine-oriented plain text.

## Recommendation for library A

- set `theme="plain"` as safe default in `_smonitor.py`,
- allow dev/qa scripts to opt into `theme="rich"` at runtime,
- keep message quality independent from theme (theme is presentation, not logic).

## You are done when

- both plain and rich themes render useful diagnostics,
- switching profile changes depth, not correctness,
- your users can understand messages without knowing SMonitor internals.
