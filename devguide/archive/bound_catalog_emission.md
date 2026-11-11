---
summary: Bind an explicit provider root for repeated catalog emission without repeated path resolution.
issue: uibcdf/smonitor#63
status: resolved
opened: 2026-11-10
closed: 2026-11-10
verification: measured
area: [integration, performance]
guard: tests/test_bound_provider.py
normative: docs/content/user/integrating-your-library.md
blocked_by: []
supersedes: []
---

# Repeated catalog emission

The owner issue retains the isolated public 0.22.1 reproduction and immutable
PharmacophoreMT/PyUnitWizard profiles. `ensure_configured` currently resolves
the path before testing configured membership. A cache keyed only by the
unresolved string can change relative/cwd and retargeted-symlink semantics.

Evaluate an explicit binding to a once-resolved canonical root. Repeated bound
emission should reuse the configured membership under its existing lock and
respect reset, manager replacement, first-use bootstrap, declaration-only
registration and forced provider policy. Ordinary path inputs keep resolving
their current filesystem target. Consumers own adoption of the bound route.

## Implemented outcome

Warm-bound bootstrap and declaration-only emissions make zero Path.resolve calls in a 100-call control. Reset/force, manager replacement, concurrent first use, cwd and symlink cases pass.

The linked maintained contract states the supported input/backend and coverage
boundaries. Consumer receiving is coordinated under uibcdf/molsyssuite#181;
publication remains separately tracked in uibcdf/smonitor#67.
