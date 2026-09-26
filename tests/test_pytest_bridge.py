"""The optional pytest bridge keeps diagnostic identity and shared-data safety."""

from importlib.metadata import entry_points

import pytest

import smonitor
from smonitor.core.manager import _add_event_observer, _remove_event_observer
from smonitor.pytest_plugin import _ReceptorObserver

pytest_plugins = ["pytester"]


def test_bridge_emits_stable_identity_without_arbitrary_message_or_extra():
    accepted = []
    gaps = []

    def accept(config, namespace, payload):
        accepted.append((config, namespace, payload))
        return "producer-ref"

    config = object()
    observer = _ReceptorObserver(config, accept, gaps.append)
    _add_event_observer(observer)
    try:
        smonitor.configure(level="DEBUG", handlers=[], profile="agent")
        event = smonitor.emit(
            "WARNING",
            "secret=abcdefghijklmnop",
            source="example.operation",
            code="EXAMPLE-WARN-001",
            extra={
                "evidence": {"private_value": "opaque secret"},
                "severity": "moderate",
            },
        )
    finally:
        _remove_event_observer(observer)

    assert len(accepted) == 1
    assert accepted[0][0] is config
    assert accepted[0][1] == "uibcdf.smonitor@1"
    payload = accepted[0][2]
    assert payload["schema"] == "smonitor.pytest-event@1"
    assert (payload["code"], payload["signal"], payload["fingerprint"]) == (
        event["code"],
        event["source"],
        event["fingerprint"],
    )
    assert payload["diagnostic"] == {"severity": "moderate"}
    assert "message" not in payload
    assert "evidence" not in payload
    assert not gaps


def test_bridge_failure_marks_gap_and_preserves_smonitor_emission():
    gaps = []

    def reject(config, namespace, payload):
        raise RuntimeError("producer unavailable")

    config = object()
    observer = _ReceptorObserver(config, reject, gaps.append)
    _add_event_observer(observer)
    try:
        smonitor.configure(level="DEBUG", handlers=[])
        event = smonitor.emit("ERROR", "diagnostic", code="EXAMPLE-ERROR-001")
    finally:
        _remove_event_observer(observer)

    assert event["code"] == "EXAMPLE-ERROR-001"
    assert gaps == [config]


@pytest.mark.parametrize("distributed", [False, True])
def test_receptor_artifact_correlates_smonitor_events(pytester, distributed):
    pytest.importorskip("pytest_receptor.extensions")
    if distributed:
        pytest.importorskip("xdist")
    from pytest_receptor import read_artifact

    pytester.makeconftest(
        """
        import pytest
        import smonitor

        @pytest.fixture
        def diagnostics():
            smonitor.configure(level='DEBUG', handlers=[])
            smonitor.emit('WARNING', 'setup', code='BRIDGE-SETUP', source='proof')
            yield
            smonitor.emit('WARNING', 'teardown', code='BRIDGE-TEARDOWN', source='proof')
        """
    )
    pytester.makepyfile(
        test_diagnostics="""
        import smonitor

        def test_first(diagnostics):
            smonitor.emit('WARNING', 'call', code='BRIDGE-CALL', source='proof')

        def test_second(diagnostics):
            smonitor.emit('WARNING', 'call', code='BRIDGE-CALL', source='proof')
        """
    )
    args = ["--receptor=llm", "--receptor-events=events.jsonl"]
    if not any(ep.name == "smonitor" for ep in entry_points(group="pytest11")):
        args[:0] = ["-p", "smonitor.pytest_plugin"]
    if distributed:
        args.extend(("-n", "2"))
    result = pytester.runpytest(*args)

    assert result.ret == pytest.ExitCode.OK
    artifact = read_artifact(pytester.path / "events.jsonl")
    assert artifact.complete and artifact.integrity_valid
    extensions = [event.data for event in artifact.events if event.type == "extension"]
    assert len(extensions) == 6
    assert artifact.final.data["extensions"] == {"recorded": 6, "dropped": 0, "incomplete": False}
    assert {(event["phase"], event["payload"]["code"]) for event in extensions} == {
        ("setup", "BRIDGE-SETUP"),
        ("call", "BRIDGE-CALL"),
        ("teardown", "BRIDGE-TEARDOWN"),
    }
    for event in extensions:
        assert event["nodeid"].startswith("test_diagnostics.py::")
        if distributed:
            assert event["worker_id"] in {"gw0", "gw1"}
        assert event["attempt"] == 1
        assert event["emitted_during"]
