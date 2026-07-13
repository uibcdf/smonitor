from __future__ import annotations

import inspect

import pytest

import smonitor
from smonitor.core import decorator as decorator_module


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
