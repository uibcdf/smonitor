# Integration API (Advanced)

This page covers integration helpers beyond basic `@signal` usage.

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

This loads `_smonitor.py` defaults and avoids repeated ad-hoc configure calls.

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
