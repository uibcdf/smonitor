# User Guide

This guide is for developers who want to integrate **SMonitor** into their own scientific Python library.

If you follow this section in order, you will end with:
- clear diagnostics for users,
- traceable signals for developers and QA,
- a repeatable integration you can ship safely.

## Who this is for

Use this guide if you maintain a library and need to improve:
- warning and error clarity,
- debugging speed,
- support turnaround,
- consistency across modules.

## What you will build

By the end of this path you will have:
- `_smonitor.py` in your package root,
- a catalog in `A/_private/smonitor/catalog.py`,
- project metadata in `A/_private/smonitor/meta.py`,
- warning/error helpers using `DiagnosticBundle`,
- `@signal` instrumentation in key entry points,
- tests and release checks for your diagnostics layer.

## Suggested reading path

1. [Quick Start](quickstart.md): get a first working integration in minutes.
2. [Mini Library Walkthrough](mini-library-walkthrough.md): full end-to-end example.
3. [Configuration](configuration.md): profile, policy, and precedence model.
4. [Integrating Your Library](integrating-your-library.md): migration strategy for real codebases.
5. [Edge Cases](edge-cases.md): avoid common integration mistakes.
6. [Troubleshooting](troubleshooting.md): diagnose common failures fast.
7. [Audit CLI](audit-cli.md): run practical validation checks.
8. [Bundles and Export](bundles-and-export.md): produce reproducible diagnostics artifacts.
9. [Message Style by Profile](message-style-by-profile.md): design clear profile-aware communication.
10. [Production Checklist](production-checklist.md): ship with confidence.
11. [FAQ](faq.md): quick answers to common design questions.

## Canonical contract

Keep this file in view while integrating:
- [SMONITOR_GUIDE.md](https://github.com/uibcdf/smonitor/blob/main/standards/SMONITOR_GUIDE.md)

```{toctree}
:maxdepth: 1
:hidden:

quickstart.md
mini-library-walkthrough.md
configuration.md
integrating-your-library.md
edge-cases.md
troubleshooting.md
audit-cli.md
bundles-and-export.md
message-style-by-profile.md
production-checklist.md
faq.md
```
