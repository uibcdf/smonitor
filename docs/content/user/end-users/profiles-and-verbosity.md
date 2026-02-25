# Choosing Profiles and Verbosity

Many libraries expose a way to run with different diagnostics profiles.

Common profiles:
- `user`: concise and friendly output,
- `dev`: more technical context,
- `qa`/`debug`: deeper diagnostics for troubleshooting.

## Recommendation

- default to `user` for normal workflows,
- switch to `dev` or `debug` only when troubleshooting.

## Typical runtime override (if `A` exposes it)

```python
import smonitor

smonitor.configure(profile="dev", level="INFO")
```

If `A` does not expose profile controls directly, ask maintainers for the
recommended method in that library.

Some libraries intentionally keep SMonitor controls internal and only expose
their own high-level verbosity/configuration flags. In that case, use the
library-specific mechanism and keep SMonitor details transparent.
