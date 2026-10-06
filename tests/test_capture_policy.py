import asyncio
import json
import logging
import warnings
from concurrent.futures import ThreadPoolExecutor
from contextvars import Context, copy_context
from dataclasses import FrozenInstanceError

import pytest

import smonitor
from smonitor._diagnostics import CapturePolicyError
from smonitor.core.capture import DETAILED
from smonitor.core.context import _context_stack, pop_frame, push_frame
from smonitor.core.manager import _add_event_observer, _remove_event_observer
from smonitor.handlers.memory import MemoryHandler
from smonitor.integrations import CatalogException


class Opaque:
    def __init__(self):
        self.calls = 0

    def __repr__(self):
        self.calls += 1
        return "OPAQUE_PAYLOAD_MARKER"


class NativeFailure(ValueError):
    def __init__(self):
        super().__init__("NATIVE_PAYLOAD_MARKER")
        self.calls = 0

    def __str__(self):
        self.calls += 1
        return super().__str__()


def configured(**kwargs):
    handler = MemoryHandler()
    manager = smonitor.configure(
        level="DEBUG",
        profile="user",
        handlers=[handler],
        capture_logging=False,
        capture_warnings=False,
        event_buffer_size=100,
        **kwargs,
    )
    return manager, handler


@pytest.mark.parametrize("failure", [False, True])
@pytest.mark.parametrize("args_summary", [False, True])
def test_metadata_only_prevents_collection_and_retention(failure, args_summary):
    manager, handler = configured(
        args_summary=args_summary,
        profiling=True,
        slow_signal_ms=0.000001,
        profiling_buffer_size=100,
    )
    opaque, native = Opaque(), NativeFailure()
    config = manager.config
    cause = RuntimeError("CAUSE_PAYLOAD_MARKER")
    factory_calls = []

    @smonitor.signal(
        extra_factory=lambda a, k: factory_calls.append(a) or {"raw": opaque}, tags=[opaque]
    )
    def target(value):
        if failure:
            raise native from cause
        return value

    with smonitor.diagnostic_scope(safe_extra={"operation_id": "op-1"}):
        if failure:
            with pytest.raises(NativeFailure) as caught:
                target(opaque)
            assert caught.value is native
            assert native.__cause__ is cause
            names = []
            tb = native.__traceback__
            while tb:
                names.append(tb.tb_frame.f_code.co_name)
                tb = tb.tb_next
            assert "target" in names
            event = handler.events[0]
            assert event["code"] == "SMONITOR-NATIVE-FAILURE"
            assert event["exception_type"] == "NativeFailure"
        else:
            assert target(opaque) is opaque
    assert opaque.calls == native.calls == 0
    assert factory_calls == []
    assert manager.config is config
    assert _context_stack.get() is None
    assert handler.events
    for event in handler.events:
        assert event["context"] is None
        assert event["extra"]["operation_id"] == "op-1"
    retained = json.dumps(
        [handler.events, manager.recent_events(), manager.report(), smonitor.collect_bundle()]
    )
    for marker in ("OPAQUE_PAYLOAD_MARKER", "NATIVE_PAYLOAD_MARKER", "CAUSE_PAYLOAD_MARKER"):
        assert marker not in retained
    assert smonitor.get_capture_policy() == DETAILED


def test_explicit_metadata_emission_excludes_unsafe_enclosing_frames():
    manager, handler = configured(args_summary=True)
    raw = Opaque()
    observed = []

    def observer(event, **kwargs):
        observed.append(event)

    _add_event_observer(observer)
    push_frame("provider", "module", args={"raw": raw}, extra={"raw": raw})
    try:
        event = smonitor.emit(
            "ERROR",
            raw,
            extra={"raw": raw},
            tags=[raw],
            metadata_only=True,
            safe_extra={"operation_id": "safe-op"},
        )
        assert event["context"] is None
        assert event["extra"]["operation_id"] == "safe-op"
        assert "raw" not in event["extra"]
        assert raw.calls == 0
        assert observed and handler.events
        assert "OPAQUE_PAYLOAD_MARKER" not in json.dumps(smonitor.collect_bundle())
    finally:
        pop_frame()
        _remove_event_observer(observer)
    assert manager.config.args_summary


def test_scopes_are_immutable_nested_and_restore_on_failure():
    with pytest.raises(FrozenInstanceError):
        smonitor.METADATA_ONLY.arguments = True
    facts = {"operation_id": "outer"}
    with smonitor.diagnostic_scope(safe_extra=facts):
        facts["operation_id"] = "changed"
        with pytest.raises(RuntimeError):
            with smonitor.diagnostic_scope(DETAILED, safe_extra={"attempt": 2}):
                assert smonitor.get_capture_policy() == smonitor.METADATA_ONLY
                event = smonitor.emit("ERROR", "discarded")
                assert event["extra"]["operation_id"] == "outer"
                assert event["extra"]["attempt"] == 2
                raise RuntimeError()
        assert smonitor.get_capture_policy() == smonitor.METADATA_ONLY
    assert smonitor.get_capture_policy() == DETAILED


def test_independent_controls_filter_inherited_frames_before_serialization():
    manager, handler = configured(args_summary=True)
    raw = Opaque()
    push_frame("outer", "provider", args={"value": raw}, extra={"value": raw})
    try:
        policy = smonitor.CapturePolicy(arguments=False, extra=False)
        with smonitor.diagnostic_scope(policy):
            smonitor.emit("WARNING", "allowed text", extra={"raw": raw})
        frame = handler.events[0]["context"]["frames"][0]
        assert frame["args"] is None and frame["extra"] is None
        assert handler.events[0]["message"] == "allowed text"
        assert raw.calls == 0
    finally:
        pop_frame()


def test_catalog_identity_and_approved_facts_without_native_text():
    manager, handler = configured()
    smonitor.configure(
        codes={
            "KNOWN": {
                "user_message": "Unsafe {raw}",
                "metadata_message": "Operation {operation_id} failed.",
                "metadata_hint": "Retry attempt {attempt}.",
            }
        }
    )
    raw = Opaque()

    @smonitor.signal(
        capture_policy=smonitor.METADATA_ONLY, safe_extra={"operation_id": "op", "attempt": 1}
    )
    def target(value):
        raise CatalogException(code="KNOWN", extra={"raw": raw}, message=raw)

    with pytest.raises(CatalogException) as caught:
        target(raw)
    assert caught.value.code == handler.events[0]["code"] == "KNOWN"
    assert handler.events[0]["message"] == "Operation op failed."
    assert handler.events[0]["extra"]["hint"] == "Retry attempt 1."
    assert raw.calls == 0
    assert "raw" not in handler.events[0]["extra"]


@pytest.mark.parametrize("value", [Opaque(), ["value"], {"nested": "value"}, float("inf"), 2**65])
def test_unapproved_metadata_is_rejected_without_conversion(value):
    with pytest.raises(CapturePolicyError):
        with smonitor.diagnostic_scope(safe_extra={"value": value}):
            pytest.fail("invalid scope entered")
    if isinstance(value, Opaque):
        assert value.calls == 0
    assert smonitor.get_capture_policy() == DETAILED


@pytest.mark.parametrize(
    "phase", ["get_manager", "record_call", "record_timing", "emit", "pop_frame"]
)
def test_fallback_cannot_stringify_or_replace_native(monkeypatch, phase):
    manager, handler = configured(profiling=True)
    native, diagnostic = NativeFailure(), NativeFailure()

    def broken(*args, **kwargs):
        raise diagnostic

    if phase in ("get_manager", "pop_frame"):
        monkeypatch.setattr("smonitor.core.decorator." + phase, broken)
    else:
        monkeypatch.setattr(manager, phase, broken)

    @smonitor.signal(capture_policy=smonitor.METADATA_ONLY)
    def target(value):
        raise native

    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        with pytest.raises(NativeFailure) as caught:
            target(Opaque())
    assert caught.value is native
    assert native.calls == diagnostic.calls == 0


def test_async_decorator_and_interleaved_scopes():
    manager, handler = configured(args_summary=True)
    raw_restricted, raw_detailed = Opaque(), Opaque()

    @smonitor.signal
    async def target(raw, barrier):
        await barrier.wait()
        await asyncio.sleep(0)
        raise NativeFailure()

    async def main():
        barrier = asyncio.Event()

        async def worker(restricted):
            policy = smonitor.METADATA_ONLY if restricted else DETAILED
            with smonitor.diagnostic_scope(policy, safe_extra={"worker": restricted}):
                with pytest.raises(NativeFailure):
                    await target(raw_restricted if restricted else raw_detailed, barrier)
                assert smonitor.get_capture_policy() == policy

        tasks = [asyncio.create_task(worker(value)) for value in (True, False)]
        barrier.set()
        await asyncio.gather(*tasks)

    asyncio.run(main())
    restricted = [event for event in handler.events if event["extra"]["worker"] is True]
    detailed = [event for event in handler.events if event["extra"]["worker"] is False]
    assert restricted[0]["context"] is None
    assert detailed[0]["context"] is not None
    assert raw_restricted.calls == 0 and raw_detailed.calls > 0
    assert smonitor.get_capture_policy() == DETAILED
    assert _context_stack.get() is None


def test_thread_policy_requires_explicit_context_propagation():
    configured()
    with ThreadPoolExecutor(max_workers=2) as pool:
        with smonitor.diagnostic_scope():
            inherited = copy_context()
            clean = Context()
            left = pool.submit(inherited.run, smonitor.get_capture_policy)
            right = pool.submit(clean.run, smonitor.get_capture_policy)
            assert left.result() == smonitor.METADATA_ONLY
            assert right.result() == DETAILED
        assert pool.submit(Context().run, smonitor.get_capture_policy).result() == DETAILED


def test_logging_capture_does_not_format_opaque_payload():
    manager, handler = configured()
    from smonitor.emitters.logging import SmonitorLoggingHandler

    raw = Opaque()
    record = logging.LogRecord("provider", logging.ERROR, __file__, 1, "%r", (raw,), None)
    with smonitor.diagnostic_scope():
        SmonitorLoggingHandler().emit(record)
    assert raw.calls == 0
    assert handler.events[0]["context"] is None


def test_default_error_summary_and_exception_text_remain_available():
    manager, handler = configured(args_summary=False)
    raw, native = Opaque(), NativeFailure()

    @smonitor.signal
    def target(value):
        raise native

    with pytest.raises(NativeFailure) as caught:
        target(raw)
    assert caught.value is native
    assert raw.calls > 0 and native.calls > 0
    assert "OPAQUE_PAYLOAD_MARKER" in json.dumps(handler.events)
    assert "NATIVE_PAYLOAD_MARKER" in json.dumps(handler.events)


@pytest.mark.parametrize("mode", ["coalesce", "duplicate"])
def test_deferred_summaries_retain_capture_policy(mode):
    options = (
        {"warning_coalesce_window_s": 60}
        if mode == "coalesce"
        else {"duplicate_policy": "emit_summary"}
    )
    manager, handler = configured(**options)
    for _ in range(3):
        smonitor.emit(
            "WARNING",
            "UNAPPROVED_MESSAGE",
            source="provider",
            metadata_only=True,
            safe_extra={"operation_id": "op"},
        )
    assert len(handler.events) == 1
    raw = Opaque()
    push_frame("outer", "provider", args={"value": raw}, extra={"value": raw})
    try:
        smonitor.collect_bundle()
    finally:
        pop_frame()
    assert len(handler.events) == 2
    summary = handler.events[-1]
    assert summary["context"] is None
    assert summary["extra"]["operation_id"] == "op"
    assert summary["extra"]["suppressed_count"] == 2
    assert raw.calls == 0
    assert "UNAPPROVED_MESSAGE" not in json.dumps([handler.events, manager.report()])


def test_route_transforms_cannot_reintroduce_unapproved_payloads():
    manager, handler = configured()
    raw = Opaque()
    smonitor.configure(
        routes=[
            {
                "when": {"source": "provider"},
                "send_to": ["memory"],
                "set_extra": {"raw": raw},
                "set": {"message": raw},
                "add_tags": [raw],
            }
        ]
    )
    event = smonitor.emit("ERROR", "ignored", source="provider", metadata_only=True)
    assert event["message"] != raw
    assert "raw" not in event["extra"] and event["tags"] is None
    assert handler.events
    assert raw.calls == 0


def test_full_safe_metadata_budget_does_not_break_slow_signals():
    manager, handler = configured(profiling=True, slow_signal_ms=0.000001)

    @smonitor.signal(
        capture_policy=smonitor.METADATA_ONLY,
        safe_extra={f"key-{index}": index for index in range(32)},
    )
    def target():
        return 1

    assert target() == 1
    assert handler.events[-1]["code"] == "SMONITOR-SIGNAL-SLOW"


def test_promoted_fallback_warning_preserves_success(monkeypatch):
    manager, handler = configured(profiling=True)
    diagnostic = NativeFailure()

    def broken(*args, **kwargs):
        raise diagnostic

    monkeypatch.setattr(manager, "record_timing", broken)

    @smonitor.signal(capture_policy=smonitor.METADATA_ONLY)
    def target():
        return 17

    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        assert target() == 17
    assert diagnostic.calls == 0


def test_restricted_span_discards_payloads_and_preserves_native(monkeypatch):
    from smonitor.profiling import span

    manager, handler = configured(profiling=True, profiling_buffer_size=10)
    raw, native = Opaque(), NativeFailure()
    with smonitor.diagnostic_scope():
        with span("operation", value=raw):
            pass
    assert "OPAQUE_PAYLOAD_MARKER" not in json.dumps(manager.report())

    def broken(*args, **kwargs):
        raise NativeFailure()

    monkeypatch.setattr(manager, "record_timing", broken)
    with smonitor.diagnostic_scope(), warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        with pytest.raises(NativeFailure) as caught:
            with span("operation", value=raw):
                raise native
    assert caught.value is native
    assert raw.calls == native.calls == 0


def test_exported_bundle_retains_only_approved_event_payload(tmp_path):
    manager, handler = configured()
    raw = Opaque()
    smonitor.emit(
        "ERROR",
        raw,
        extra={"value": raw},
        metadata_only=True,
        safe_extra={"operation_id": "export-op"},
    )
    smonitor.export_bundle(tmp_path / "bundle")
    files = list((tmp_path / "bundle").rglob("*.json")) + list(
        (tmp_path / "bundle").rglob("*.jsonl")
    )
    assert files
    text = "\n".join(path.read_text() for path in files)
    assert "export-op" in text and "OPAQUE_PAYLOAD_MARKER" not in text
    assert raw.calls == 0


def test_thread_calls_keep_independent_capture_permissions():
    from threading import Barrier

    manager, handler = configured(args_summary=True)
    barrier = Barrier(2)
    restricted, detailed = Opaque(), Opaque()

    @smonitor.signal
    def target(raw):
        barrier.wait()
        raise NativeFailure()

    def worker(raw, policy):
        with smonitor.diagnostic_scope(policy):
            with pytest.raises(NativeFailure):
                target(raw)

    with ThreadPoolExecutor(max_workers=2) as pool:
        left = pool.submit(Context().run, worker, restricted, smonitor.METADATA_ONLY)
        right = pool.submit(Context().run, worker, detailed, DETAILED)
        left.result()
        right.result()
    assert restricted.calls == 0 and detailed.calls > 0
    events = [event for event in handler.events if event["code"] == "SMONITOR-NATIVE-FAILURE"]
    assert events[0]["context"] is None


def test_failed_repr_does_not_prevent_native_event():
    manager, handler = configured(args_summary=False)

    class Broken:
        def __repr__(self):
            raise RuntimeError("repr failure")

    native = ValueError("native failure")

    @smonitor.signal
    def target(raw):
        raise native

    with pytest.warns(RuntimeWarning, match="argument summary failed"):
        with pytest.raises(ValueError) as caught:
            target(Broken())
    assert caught.value is native
    assert handler.events[0]["message"] == "native failure"


def test_explicit_resolution_facts_obey_independent_text_restriction():
    configured()
    smonitor.configure(codes={"SAFE": {"message": "Operation {operation_id} failed."}})
    raw = Opaque()
    with smonitor.diagnostic_scope(smonitor.CapturePolicy(exception_text=False)):
        message, hint = smonitor.resolve(
            code="SAFE",
            message=raw,
            extra={"operation_id": raw},
            safe_extra={"operation_id": "approved"},
        )
    assert message == "Operation approved failed."
    assert raw.calls == 0


@pytest.mark.parametrize("profiling", [False, True])
def test_span_setup_failure_and_disabled_span_preserve_operation(monkeypatch, profiling):
    from smonitor.profiling import span

    configured(profiling=profiling)
    native = NativeFailure()
    if profiling:

        def broken():
            raise NativeFailure()

        monkeypatch.setattr("smonitor.profiling.get_manager", broken)
    with smonitor.diagnostic_scope(), warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        with pytest.raises(NativeFailure) as caught:
            with span("operation"):
                raise native
    assert caught.value is native
    assert native.calls == 0


def test_metadata_only_does_not_invoke_native_exception_setters():
    configured()

    class SetterFailure(NativeFailure):
        def __setattr__(self, name, value):
            if name == "__smonitor_emitted__":
                str(self)
            super().__setattr__(name, value)

    native = SetterFailure()

    @smonitor.signal(capture_policy=smonitor.METADATA_ONLY)
    def target():
        raise native

    with pytest.raises(SetterFailure) as caught:
        target()
    assert caught.value is native
    assert native.calls == 0
