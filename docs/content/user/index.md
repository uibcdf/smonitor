# User Guide

SMonitor has two user profiles with different goals:

1. **Library integrators**: developers who implement SMonitor in a host library.
2. **Library end users**: people who use the host library and receive SMonitor messages through it.

Use the route that matches your role.

If you are evaluating adoption, start with the integrator route and then review
the end-user route to ensure your diagnostics experience is clear from both sides.

## Route A: Library Integrators

Go to [Library Integrators](library-integrators/index.md).

In this route you will learn how to:
- add `_smonitor.py` and catalog contracts,
- instrument API boundaries with `@signal`,
- validate and ship diagnostics safely.

## Route B: Library End Users

Go to [Library End Users](end-users/index.md).

In this route you will learn how to:
- interpret messages shown by libraries using SMonitor,
- improve your local diagnostics experience (profiles, verbosity),
- report reproducible issues efficiently.

Both routes converge on the same goal: better diagnostics quality with lower
support cost and better QA reproducibility.

```{toctree}
:maxdepth: 1
:hidden:

library-integrators/index.md
end-users/index.md
```
