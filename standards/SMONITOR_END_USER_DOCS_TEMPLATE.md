# Template: End-User Diagnostics Section for Host library

Use this template in host library documentation (for example, user guide, FAQ,
or troubleshooting). Replace placeholders before publishing.

---

## Diagnostics in {{HOST_LIBRARY_NAME}} (powered by SMonitor)

`{{HOST_LIBRARY_NAME}}` uses SMonitor to provide warnings and errors that are meant to
help you solve issues faster.

These messages are guidance, not blame.

### How to interpret messages

- `WARNING`: operation usually continues, but quality/ambiguity should be reviewed.
- `ERROR`: operation failed for current input/state; apply hint and retry.

### 30-second rescue flow

1. Read message and hint.
2. Apply suggested fix.
3. Retry once.

If it still fails:
- keep full message and code ID (for example `{{HOST_LIBRARY_CODE_EXAMPLE}}`),
- prepare a minimal reproducer,
- include version/environment info,
- optionally attach a redacted diagnostics bundle.

### How to get more details in {{HOST_LIBRARY_NAME}}

Use the diagnostics/verbosity controls documented by `{{HOST_LIBRARY_NAME}}`:
- {{HOST_LIBRARY_VERBOSITY_INSTRUCTIONS}}

### Where to report issues

- {{HOST_LIBRARY_ISSUES_URL}}

### Extended SMonitor end-user docs

- https://uibcdf.github.io/smonitor/content/user/end-users/index.html

---

## Maintainer notes (remove from user-facing docs)

- Fill placeholders:
  - `{{HOST_LIBRARY_NAME}}`
  - `{{HOST_LIBRARY_CODE_EXAMPLE}}`
  - `{{HOST_LIBRARY_VERBOSITY_INSTRUCTIONS}}`
  - `{{HOST_LIBRARY_ISSUES_URL}}`
- Keep this section aligned with:
  - `SMONITOR_END_USER_GUIDE_FOR_LIBRARIES.md`
  - `SMONITOR_END_USER_RESCUE_CARD.md`
- Add sync metadata header in your copy, for example:
  - `Source: smonitor/standards/SMONITOR_END_USER_DOCS_TEMPLATE.md`
  - `Synced from: smonitor@<tag-or-commit>`
