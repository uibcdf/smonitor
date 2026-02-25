# Support Policy

This document defines how support is handled for the **SMonitor** ecosystem.

## Scope

We support:
- Core APIs documented in the public docs.
- Reproducible bugs in stable releases.
- Configuration and integration issues aligned with `SPEC_SMONITOR.md`.

We do **not** guarantee:
- Debugging unpublished forks or private environments with no reproduction case.
- Performance optimization requests without measurable baseline and reproduction.

## Severity Levels

- **S1 (Critical)**: Core functionality broken. Target response: same day.
- **S2 (Major)**: Key workflow broken. Target response: 48h.
- **S3 (Minor)**: Non-blocking issue. Target response: best effort.

## Required Info for Bug Reports

Before opening an issue, provide:
- Version (`smonitor.__version__`)
- OS and Python version
- Minimal reproducible case
- Optional: local smonitor bundle export (preferred)

## Recommended Workflow

1. Reproduce with the latest release.
2. Collect a local diagnostics bundle.
3. Open an issue with severity and reproduction details.

## Response Policy

- Issues are prioritized by severity and reproducibility.
- If information is missing, issue state becomes `needs-info`.
- If no response in 14 days after `needs-info`, the issue may be closed.

## Telemetry (Opt-in)

Telemetry is **off by default**.
If enabled, only minimal, anonymized data should be sent under documented schema.

## Roadmap Alignment

Priority is given to issues that:
- affect multiple libraries,
- have high user/developer impact,
- include reproducible evidence.

## Related Documents

- Product and architecture decisions: `SPEC_SMONITOR.md`
- Development practices: `devguide/README.md`
