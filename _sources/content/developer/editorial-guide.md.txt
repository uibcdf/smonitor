# Editorial Guide

This guide defines how we write documentation and contributor-facing text in SMonitor.

Goal: make docs readable, explicit, and easy to follow for both humans and coding agents.

## Core principles

1. Narrative first

Write as a guided path, not as disconnected notes. The reader should always know what to do next.

2. Explicit over terse

Prefer clear explanation and concrete examples over short but ambiguous statements.

3. Contract-aware writing

When a behavior is contractual, link the canonical source (for example `SMONITOR_GUIDE.md`) and avoid conflicting paraphrases.

4. Operational language

Use wording that helps execution: what to run, what to verify, and what outcome to expect.

## Structure rules

- Start each page with scope and intent.
- Use short sections with clear headings.
- Add cross-links to adjacent pages when a concept depends on another.
- Keep examples realistic and aligned with current API.

## Style rules

- Keep tone direct and technical.
- Avoid marketing language.
- Prefer active voice.
- Avoid unexplained acronyms.

## Maintenance rules

When code behavior changes:
- update User docs if integration behavior changes;
- update Developers docs if contributor workflow or architecture changes;
- update canonical guides when contracts change.
