# SMonitor End-User Rescue Card

Use this short block in host library docs, FAQ, or troubleshooting page.

## When you see a warning or error in the host library

1. Read the message and hint.
2. Apply the suggested fix.
3. Retry once.

If it still fails:
- copy full message and code ID,
- prepare a minimal reproducer,
- share environment details,
- optionally attach a redacted diagnostics bundle.

Rule of thumb:
- `WARNING` -> often continue, then refine.
- `ERROR` -> fix input/state, then retry or report.

More details:
- https://uibcdf.github.io/smonitor/content/user/end-users/index.html
