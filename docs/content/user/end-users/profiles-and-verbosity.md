# Choosing Profiles and Verbosity

Many libraries expose a way to run with different diagnostics profiles.

Common profiles:
- `user`: concise and friendly output,
- `dev`: more technical context,
- `qa`/`debug`: deeper diagnostics for troubleshooting.

## Recommendation

- default to `user` for normal workflows,
- switch to `dev` or `debug` only when troubleshooting.

## First choice: use library `A` controls

Prefer controls documented by library `A` (for example, its own verbosity or
debug flags). In many projects, this is the intended user-facing interface.

## Typical runtime override (only if `A` explicitly exposes SMonitor controls)

```python
import smonitor

smonitor.configure(profile="dev", level="INFO")
```

If `A` does not expose SMonitor profile controls directly, do not force it.
Use the method recommended by maintainers of `A`.

Some libraries intentionally keep SMonitor controls internal and only expose
their own high-level verbosity/configuration flags. In that case, use the
library-specific mechanism and keep SMonitor details transparent.
