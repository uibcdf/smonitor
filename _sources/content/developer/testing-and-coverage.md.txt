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

## Pytest diagnostic artifact

Install the optional `smonitor[pytest]` extra, which requires Pytest Receptor
1.2 or newer, then opt in to its canonical JSONL artifact:

For Conda installations, install `smonitor`, `pytest`, and
`pytest-receptor>=1.2,<2` from `uibcdf` and `conda-forge`.

```bash
mkdir -p .pytest-receptor
python -m pytest --receptor=llm --receptor-events=.pytest-receptor/events.jsonl
```

SMonitor's pytest plugin loads only when pytest runs. With the artifact option
enabled, it sends structured diagnostic identity into namespaced receptor
records. Each record carries the SMonitor code, signal, fingerprint, run and
correlation IDs, plus pytest's test, phase, worker, and attempt. The bridge
does not alter pytest outcomes or create a second reporter. It omits free-form
messages, context, and arbitrary `extra` fields from the shared artifact by
default; the standalone SMonitor bundle remains available separately. The
receptor marks rejected or lost extension evidence as incomplete without
turning a failing test into a pass. Neither package uploads artifacts.

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
