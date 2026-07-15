from pathlib import Path
from dataclasses import replace

import pytest
import smonitor
from smonitor.core.manager import ManagerConfig, get_manager


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


def test_manager_config_containers_are_deeply_immutable_and_unaliased():
    silence = ["pkg"]
    hooks = [lambda: {"ok": True}]
    config = ManagerConfig(silence=silence, profiling_hooks=hooks)

    silence.append("other")
    hooks.clear()
    assert config.silence == ("pkg",)
    assert len(config.profiling_hooks or ()) == 1
    with pytest.raises(AttributeError):
        config.silence.append("mutated")
    with pytest.raises(AttributeError):
        config.profiling_hooks.append(lambda: {})  # type: ignore[union-attr]

    copied = replace(config, silence=["replacement"])
    assert copied.silence == ("replacement",)


def test_configure_accepts_list_containers_without_exposing_mutability():
    hook = lambda: {"hook": "ran"}
    manager = smonitor.configure(
        profile="user",
        handlers=[],
        silence=["pkg"],
        profiling_hooks=[hook],
    )

    assert manager.config.silence == ("pkg",)
    assert manager.config.profiling_hooks == (hook,)
    assert manager.report()["profiling_meta"]["hook"] == "ran"
    assert smonitor.emit("WARNING", "x", source="pkg.mod", code="C1") == {}
