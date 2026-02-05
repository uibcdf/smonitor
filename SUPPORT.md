# Support Policy (Template)

This document defines how support is handled for the Smontor ecosystem.
Adapt it per project if needed.

## Scope

We support:
- Core APIs documented in the public docs.
- Reproducible bugs in stable releases.

We do **not** guarantee:
- Debugging of unpublished forks or private data.
- Performance issues without a reproducible case.

## Severity Levels

- **S1 (Critical)**: Core functionality broken. Target response: same day.
- **S2 (Major)**: Key workflow broken. Target response: 48h.
- **S3 (Minor)**: Non-blocking issues. Target response: best effort.

## Required Info for Bugs

Before opening an issue, please provide:

- Version (`smonitor.__version__`)
- OS and Python version
- Minimal reproduction
- Optional: smonitor export bundle (preferred)

## Recommended Workflow

1. Reproduce with latest release.
2. Collect a local bundle:

```
# example (future)
# smonitor export --last 1h
```

3. Open an issue with severity label.

## Response Policy

- We respond in order of severity.
- If information is missing, the issue is set to `needs-info`.
- If no response in 14 days, the issue may be closed.

## Telemetry (Opt-in)

Telemetry is **off by default**.
If enabled, only anonymized and minimal data is sent.

## Roadmap Alignment

We prioritize issues that:
- affect multiple libraries,
- have high impact,
- are backed by reproducible evidence.
