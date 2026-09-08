# Testing and Coverage

SMonitor is infrastructure. Regressions are expensive downstream, so tests must cover behavior, not only lines.

## 1. Minimum local test command

```bash
pytest -q
```

## 2. Coverage command

```bash
pytest --cov=smonitor --cov-report=term-missing
```

## 3. Architecture audit command

```bash
pytest -q tests/test_core.py tests/test_integrations.py tests/test_policy.py
```

## 4. Areas that should always be covered

- configuration precedence (`configure` > env vars > `_smonitor.py`),
- event emission and profile-aware resolution,
- SIGNALS/CODES validation behavior in `dev` and `qa`,
- handler robustness (including degraded-handler paths),
- integrations helpers (`ensure_configured`, `emit_from_catalog`),
- bundle export and CLI smoke flows.

## 5. Test design guidance

Prefer tests that assert user-visible behavior:
- exception class and message quality;
- actionable install hints;
- deterministic output for introspection APIs.

Avoid brittle tests tightly coupled to internal implementation details unless those details are part of the contract.
