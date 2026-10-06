# Integration API (Advanced)

This page covers integration helpers beyond basic `@signal` usage.

For bounded diagnostics without argument `repr`, native exception text or inherited
payloads, see [scoped diagnostic capture](scoped-capture.md).

## `DiagnosticBundle`

Use `DiagnosticBundle` to centralize warning/error emission from catalog
contracts and avoid hardcoded message strings.

```python
from smonitor.integrations import DiagnosticBundle

bundle = DiagnosticBundle(CATALOG, META, PACKAGE_ROOT)
warn = bundle.warn
warn_once = bundle.warn_once
resolve = bundle.resolve
```

`warn()` and `warn_once()` also raise ordinary Python warnings. Their
`stacklevel` counts application frames and skips SMonitor's `@signal` wrapper,
so the default value attributes a warning to the caller of the library function.
Plain `warnings.warn()` inside a decorated function still counts that wrapper;
adjust its `stacklevel` when using Python's warning API directly.

When to use:
- whenever the host library emits repeated warning families,
- when you need stable `code` + templated message/hint resolution.

## `emit_from_catalog`

Use this helper when you want direct catalog emission without custom wrappers.

```python
from smonitor.integrations import emit_from_catalog

emit_from_catalog(
    CATALOG,
    code="MYLIB-W001",
    source="mylib.select",
    extra={"selection": "all"},
)
```

## `CatalogException` and `CatalogWarning`

Use these classes to keep semantic exception/warning types while inheriting
catalog-backed message quality.

Recommended pattern:
- map each domain exception to one stable catalog code,
- preserve existing exception class hierarchy,
- keep user hints in catalog templates, not in ad-hoc `raise` strings.

## `ensure_configured`

Call once at package startup:

```python
from smonitor.integrations import ensure_configured
ensure_configured(PACKAGE_ROOT)
```

This registers the package's exact `_smonitor.py` catalog and signals. If the
application has already called `configure()`, its entire runtime policy is
preserved. Otherwise the helper bootstraps from the application's discovered
configuration, or the provider's defaults when none exists. The first bootstrap
selects policy; subsequent provider imports only register declarations. Environment
overrides keep their existing precedence.

Applications can explicitly apply a provider's recommendations with
`ensure_configured(PACKAGE_ROOT, use_provider_policy=True)`. This intentionally
reconfigures runtime policy, even after a previous import.

## `register_provider`

For libraries that only supply diagnostics, prefer:

```python
from smonitor.integrations import register_provider
register_provider(PACKAGE_ROOT, provider="mylib")
```

Registration never installs handlers or bridges and never changes application
policy. It validates declarations, then merges them atomically under a lock.
Identical repeated registrations and identical shared definitions are accepted.
Conflicting code/signal definitions reject the entire registration with
`ProviderRegistrationError` (`SMONITOR-PROVIDER-CONFLICT`); changing an existing
provider identity's declarations raises `SMONITOR-PROVIDER-IDENTITY`. Invalid
declarations raise `SMONITOR-PROVIDER-INVALID`. Loader failures propagate before
registration. Provider identities default to the resolved package directory.
Use unique, namespaced codes and signal names; explicit application catalog
overrides through `configure()` retain their existing behavior.

`get_manager().get_providers()` returns detached declarations, provenance and
unapplied recommendations. To render for another audience without reconfiguration,
use `smonitor.resolve(code="MYLIB-W001", profile="agent", extra={...})`.

## `context_extra`

Use `context_extra(...)` when a host library repeatedly assembles structured
diagnostic payloads and wants a stable cross-library contract.

```python
from smonitor.integrations import context_extra

extra = context_extra(
    caller="mylib.io.download_structure",
    resource="181l.pdb",
    provider="RCSB",
    operation="download",
    retry_attempt=2,
    retry_max=5,
    failure_class="network",
    incident_kind="network",
    recommended_action="retry",
    next_step="check-network",
    evidence={"expected": "download ok", "observed": "timeout"},
)
```

Use it for:
- shared context keys (`caller`, `resource`, `provider`, `operation`);
- retry/causal metadata;
- decision metadata;
- compact structured `evidence`.

This keeps downstream `normalized` payloads predictable for QA, support, and agents.

## `reset_configured_packages` (test-only)

Use this helper in tests to reset integration state between scenarios.

## Practical rule

Keep functional logic in SMonitor and keep library-specific data in
`mylib/_private/smonitor/` (catalog + meta). This minimizes drift and keeps
ecosystem integrations uniform.
