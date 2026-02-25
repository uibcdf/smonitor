# Library Integrators

This route is for developers integrating SMonitor into their own host library.

## Outcome

By the end of this route you should have:
- `_smonitor.py` in `mylib/`,
- catalog and metadata under `mylib/_private/smonitor/`,
- `@signal` instrumentation on relevant API boundaries,
- release checks for diagnostics quality.

## What SMonitor gives you immediately

- clear user-facing warnings/errors with actionable hints,
- optional rich visual output (`theme="rich"`),
- policy-based routing/filtering to reduce noise,
- lightweight profiling and timeline export,
- local diagnostic bundles for reproducible support,
- strict validation modes for QA (`strict_signals`, `strict_schema`).

## Important path convention

When this route says "package root", it means the root of your Python package,
not the repository root.

If your package is `mylib`, use:
- `mylib/_smonitor.py`
- `mylib/_private/smonitor/...`

## Recommended sequence

1. [Quick Start](../quickstart.md)
2. [First Runnable Integration](first-runnable-integration.md)
3. [Mini Library Walkthrough](../mini-library-walkthrough.md)
4. [Configuration](../configuration.md)
5. [Integrating Your Library](../integrating-your-library.md)
6. [Edge Cases](../edge-cases.md)
7. [Troubleshooting](../troubleshooting.md)
8. [Audit CLI](../audit-cli.md)
9. [Bundles and Export](../bundles-and-export.md)
10. [Visual Output and Themes](../visual-output-and-themes.md)
11. [Profiling in Your Library](../profiling-in-your-library.md)
12. [Integration Testing Template](integration-testing-template.md)
13. [Profile Decision Matrix](profile-decision-matrix.md)
14. [Handlers and Routing Patterns](handlers-and-routing.md)
15. [Integration API (Advanced)](integration-api-advanced.md)
16. [AI Agents Workflow](ai-agents-workflow.md)
17. [Message Style by Profile](../message-style-by-profile.md)
18. [Production Checklist](../production-checklist.md)
19. [FAQ](../faq.md)
20. [End-User Docs Pack for Host-Library Maintainers](../end-users/for-library-maintainers.md)

## Canonical contract

- [SMONITOR_GUIDE.md](https://github.com/uibcdf/smonitor/blob/main/standards/SMONITOR_GUIDE.md)
- [SMONITOR_END_USER_GUIDE_FOR_LIBRARIES.md](https://github.com/uibcdf/smonitor/blob/main/standards/SMONITOR_END_USER_GUIDE_FOR_LIBRARIES.md)
- [SMONITOR_END_USER_RESCUE_CARD.md](https://github.com/uibcdf/smonitor/blob/main/standards/SMONITOR_END_USER_RESCUE_CARD.md)
- [SMONITOR_END_USER_DOCS_TEMPLATE.md](https://github.com/uibcdf/smonitor/blob/main/standards/SMONITOR_END_USER_DOCS_TEMPLATE.md)
- [SMONITOR_END_USER_DOCS_ADOPTION_CHECKLIST.md](https://github.com/uibcdf/smonitor/blob/main/standards/SMONITOR_END_USER_DOCS_ADOPTION_CHECKLIST.md)
- [SMONITOR_END_USER_DOCS_SYNC_POLICY.md](https://github.com/uibcdf/smonitor/blob/main/standards/SMONITOR_END_USER_DOCS_SYNC_POLICY.md)

```{toctree}
:maxdepth: 1
:hidden:

../quickstart.md
first-runnable-integration.md
../mini-library-walkthrough.md
../configuration.md
../integrating-your-library.md
../edge-cases.md
../troubleshooting.md
../audit-cli.md
../bundles-and-export.md
../visual-output-and-themes.md
../profiling-in-your-library.md
integration-testing-template.md
profile-decision-matrix.md
handlers-and-routing.md
integration-api-advanced.md
ai-agents-workflow.md
../message-style-by-profile.md
../production-checklist.md
../faq.md
```
