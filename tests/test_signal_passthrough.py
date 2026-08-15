from __future__ import annotations

import inspect
from dataclasses import FrozenInstanceError, replace

import pytest

import smonitor
from smonitor.core import decorator as decorator_module
from smonitor.core import manager as manager_module


class Fluent:
    def set_color(self, color):
        self.color = color
        return self


def test_signal_preserves_return_type_and_signature_when_enabled():
    smonitor.configure(enabled=True, profiling=False, args_summary=True)

    @smonitor.signal(tags=["api"])
    def make_layer(value: int, *, label: str = "x") -> Fluent:
        return Fluent()

    result = make_layer(1, label="site").set_color("red")

    assert isinstance(result, Fluent)
    assert result.color == "red"
    assert list(inspect.signature(make_layer).parameters) == ["value", "label"]


def test_signal_extra_factory_failure_does_not_break_user_call():
    smonitor.configure(enabled=True, profiling=False, args_summary=True)

    def broken_extra(_args, _kwargs):
        raise RuntimeError("extra failed")

    @smonitor.signal(tags=["api"], extra_factory=broken_extra)
    def make_layer() -> Fluent:
        return Fluent()

    with pytest.warns(RuntimeWarning, match="extra_factory failed"):
        result = make_layer().set_color("blue")

    assert isinstance(result, Fluent)
    assert result.color == "blue"


def test_signal_internal_emit_failure_does_not_mask_original_exception(monkeypatch):
    smonitor.configure(enabled=True, profiling=False, args_summary=True)
    manager = smonitor.get_manager()

    def broken_emit(*_args, **_kwargs):
        raise RuntimeError("emit failed")

    monkeypatch.setattr(manager, "emit", broken_emit)

    @smonitor.signal(tags=["api"])
    def fail():
        raise ValueError("original")

    with pytest.warns(RuntimeWarning, match="exception emission failed"):
        with pytest.raises(ValueError, match="original"):
            fail()


def test_signal_finalization_failure_does_not_replace_return_value(monkeypatch):
    smonitor.configure(enabled=True, profiling=True, profiling_sample_rate=1.0)

    def broken_record_timing(*_args, **_kwargs):
        raise RuntimeError("timing failed")

    monkeypatch.setattr(smonitor.get_manager(), "record_timing", broken_record_timing)

    @smonitor.signal(tags=["api"])
    def make_layer() -> Fluent:
        return Fluent()

    with pytest.warns(RuntimeWarning, match="finalization failed"):
        result = make_layer().set_color("green")

    assert isinstance(result, Fluent)
    assert result.color == "green"


def test_signal_disabled_is_direct_passthrough():
    smonitor.configure(enabled=False)

    @smonitor.signal(tags=["api"])
    def make_layer() -> Fluent:
        return Fluent()

    result = make_layer().set_color("black")

    assert isinstance(result, Fluent)
    assert result.color == "black"


def test_signal_disabled_bypasses_manager_lookup(monkeypatch):
    smonitor.configure(enabled=False)

    @smonitor.signal
    def identity(value):
        return value

    monkeypatch.setattr(
        decorator_module,
        "get_manager",
        lambda: (_ for _ in ()).throw(AssertionError("manager lookup must be bypassed")),
    )

    assert identity(7) == 7


def test_signal_fast_path_tracks_direct_manager_reconfiguration(monkeypatch):
    manager = smonitor.get_manager()
    manager.configure(enabled=False)

    @smonitor.signal
    def identity(value):
        return value

    calls = 0
    original_get_manager = decorator_module.get_manager

    def counting_get_manager():
        nonlocal calls
        calls += 1
        return original_get_manager()

    monkeypatch.setattr(decorator_module, "get_manager", counting_get_manager)

    assert identity(1) == 1
    assert calls == 0

    manager.configure(enabled=True)
    assert identity(2) == 2
    assert calls == 1


def test_signal_fast_path_tracks_manager_enabled_assignment(monkeypatch):
    manager = smonitor.get_manager()
    manager.configure(enabled=False)
    decorator_module.runtime.set_signals_enabled(False)

    @smonitor.signal
    def identity(value):
        return value

    calls = 0
    original_get_manager = decorator_module.get_manager

    def counting_get_manager():
        nonlocal calls
        calls += 1
        return original_get_manager()

    monkeypatch.setattr(decorator_module, "get_manager", counting_get_manager)

    assert identity(1) == 1
    assert calls == 0

    manager.enabled = True
    assert identity(2) == 2
    assert calls == 1


def test_copying_config_does_not_change_active_telemetry(monkeypatch):
    manager = smonitor.get_manager()
    manager.configure(enabled=True)

    @smonitor.signal
    def identity(value):
        return value

    calls = 0
    original_get_manager = decorator_module.get_manager

    def counting_get_manager():
        nonlocal calls
        calls += 1
        return original_get_manager()

    monkeypatch.setattr(decorator_module, "get_manager", counting_get_manager)

    snapshot = replace(manager.config, enabled=False)

    assert snapshot.enabled is False
    assert manager.enabled is True
    assert decorator_module.runtime.signals_enabled is True
    assert identity(3) == 3
    assert calls == 1


def test_writing_config_enabled_fails_instead_of_being_ignored():
    manager = smonitor.get_manager()
    manager.configure(enabled=False)

    with pytest.raises(FrozenInstanceError):
        manager.config.enabled = True

    assert manager.config.enabled is False
    assert manager.enabled is False
    assert decorator_module.runtime.signals_enabled is False


def test_configure_replaces_config_once_and_syncs_enabled(monkeypatch):
    manager = smonitor.get_manager()
    replacements = 0
    original_replace = manager_module.replace

    def counting_replace(config, **changes):
        nonlocal replacements
        replacements += 1
        return original_replace(config, **changes)

    monkeypatch.setattr(manager_module, "replace", counting_replace)

    manager.configure(level="INFO", enabled=True)

    assert replacements == 1
    assert manager.config.level == "INFO"
    assert manager.enabled is True
    assert decorator_module.runtime.signals_enabled is True


# Each step the wrapper performs around the user's call is guarded on its own.
# The contract is the same for all of them: the instrumentation may fail, but
# the decorated call still runs and still returns its value, and the failure is
# reported as a RuntimeWarning rather than swallowed.


def test_signal_manager_lookup_failure_does_not_break_user_call(monkeypatch):
    smonitor.configure(enabled=True)

    def broken_get_manager():
        raise RuntimeError("manager unavailable")

    @smonitor.signal
    def make_layer() -> Fluent:
        return Fluent()

    monkeypatch.setattr(decorator_module, "get_manager", broken_get_manager)

    with pytest.warns(RuntimeWarning, match="setup failed"):
        result = make_layer().set_color("red")

    assert result.color == "red"


def test_signal_record_call_failure_does_not_break_user_call(monkeypatch):
    smonitor.configure(enabled=True)

    def broken_record_call():
        raise RuntimeError("counter failed")

    monkeypatch.setattr(smonitor.get_manager(), "record_call", broken_record_call)

    @smonitor.signal
    def make_layer() -> Fluent:
        return Fluent()

    with pytest.warns(RuntimeWarning, match="record_call failed"):
        result = make_layer().set_color("green")

    assert result.color == "green"


def test_signal_args_summary_failure_does_not_break_user_call(monkeypatch):
    smonitor.configure(enabled=True, args_summary=True)

    def broken_summarize(_args, _kwargs):
        raise RuntimeError("summary failed")

    monkeypatch.setattr(decorator_module, "_summarize_args", broken_summarize)

    @smonitor.signal
    def make_layer(value) -> Fluent:
        return Fluent()

    with pytest.warns(RuntimeWarning, match="argument summary failed"):
        result = make_layer(1).set_color("blue")

    assert result.color == "blue"


def test_signal_push_frame_failure_does_not_break_user_call(monkeypatch):
    smonitor.configure(enabled=True)

    def broken_push_frame(*_args, **_kwargs):
        raise RuntimeError("push failed")

    monkeypatch.setattr(decorator_module, "push_frame", broken_push_frame)

    @smonitor.signal
    def make_layer() -> Fluent:
        return Fluent()

    with pytest.warns(RuntimeWarning, match="push_frame failed"):
        result = make_layer().set_color("teal")

    assert result.color == "teal"


def test_signal_pop_frame_failure_does_not_break_user_call(monkeypatch):
    smonitor.configure(enabled=True)

    def broken_pop_frame():
        raise RuntimeError("pop failed")

    monkeypatch.setattr(decorator_module, "pop_frame", broken_pop_frame)

    @smonitor.signal
    def make_layer() -> Fluent:
        return Fluent()

    with pytest.warns(RuntimeWarning, match="pop_frame failed"):
        result = make_layer().set_color("amber")

    assert result.color == "amber"
