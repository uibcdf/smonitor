# Reporting Reproducible Issues

Good reports make fixes faster.

## Minimum report payload

Include:
- library version (`A` and `smonitor` if available),
- operating system and Python version,
- minimal code snippet to reproduce,
- exact error/warning message (including code ID),
- optional bundle export.

## Suggested report format

1. What you expected.
2. What happened.
3. Reproducer snippet.
4. Full message output.
5. Bundle path or attachment.

## Example short issue body

```text
Expected: selection should return only CA atoms.
Observed: warning MYLIB-W001 and empty result.
Reproducer: <10-line script>
Message: WARNING [MYLIB-W001] ...
Bundle: attached (redacted)
```
