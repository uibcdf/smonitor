from pathlib import Path

import smonitor
from smonitor.core.manager import get_manager


def test_manager_config_path_file_applies_discovered_blocks(tmp_path: Path):
    cfg_file = tmp_path / "_smonitor.py"
    cfg_file.write_text(
        "PROFILE = 'qa'\n"
        "SMONITOR = {'level': 'INFO', 'trace_depth': 2, 'event_buffer_size': 5}\n"
        "ROUTES = [{'when': {'level': 'WARNING'}, 'set': {'category': 'qa'}}]\n"
        "FILTERS = [{'when': {'code': 'DROP'}, 'drop': True}]\n"
        "CODES = {'X1': {'qa_message': 'Q msg'}}\n"
        "SIGNALS = {'pkg.fn': {'extra_required': ['a']}}\n"
    )
    manager = get_manager()
    manager.configure(handlers=[], config_path=cfg_file)
    assert manager.config.profile == "qa"
    assert manager.config.level == "INFO"
    assert manager.get_codes()["X1"]["qa_message"] == "Q msg"
    assert manager.get_signals()["pkg.fn"]["extra_required"] == ["a"]
    assert manager._policy.get_routes()
    assert manager._policy.get_filters()


def test_emit_disabled_returns_event_shape():
    manager = smonitor.configure(enabled=False, handlers=[])
    event = smonitor.emit("INFO", "x", source="s", code="C1")
    assert event["level"] == "INFO"
    assert event["source"] == "s"
    assert event["code"] == "C1"
    manager.configure(enabled=True)


def test_emit_respects_silence_prefix():
    smonitor.configure(profile="user", handlers=[], event_buffer_size=10, silence=["pkg"])
    out = smonitor.emit("WARNING", "x", source="pkg.mod", code="C1")
    assert out == {}
