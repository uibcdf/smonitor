import smonitor.core.manager as manager_module
from smonitor.core.identifiers import new_identifier
from smonitor.core.manager import get_manager


def test_new_identifier_returns_non_empty_unique_strings():
    first = new_identifier()
    second = new_identifier()

    assert isinstance(first, str)
    assert isinstance(second, str)
    assert first
    assert second
    assert first != second


def test_manager_exposes_runtime_identifiers_and_honors_overrides(monkeypatch):
    monkeypatch.setattr(manager_module, "_manager_singleton", None)
    manager = get_manager()
    runtime_ids = manager.get_runtime_identifiers()

    assert isinstance(runtime_ids["run_id"], str)
    assert isinstance(runtime_ids["session_id"], str)
    assert runtime_ids["run_id"]
    assert runtime_ids["session_id"]
    assert runtime_ids["correlation_id"] is None

    manager.configure(run_id="run-1", session_id="session-1", correlation_id="corr-1")
    runtime_ids = manager.get_runtime_identifiers()

    assert runtime_ids == {
        "run_id": "run-1",
        "session_id": "session-1",
        "correlation_id": "corr-1",
    }
