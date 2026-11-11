"""Bounded, opt-in CPython monitoring, exposed through smonitor.profiling."""

from __future__ import annotations

import gc
import inspect
import re
import sys
import threading
import time
from copy import deepcopy
from dataclasses import dataclass, field
from types import (
    BuiltinFunctionType,
    CodeType,
    FunctionType,
    MethodDescriptorType,
    MethodType,
    ModuleType,
)
from typing import Any, Mapping

from ._diagnostics import ObservationError

_ANY_RECEIVER = object()


@dataclass(frozen=True)
class NativeCallTarget:
    """A builtin/descriptor call at an exact Python caller and optional receiver.

    ``function`` is the builtin or class method descriptor, e.g. ``list.append``.
    Receiver matching uses identity only. References are held during the scope
    and are never included in its report.
    """

    caller: Any = field(repr=False)
    function: Any = field(repr=False)
    receiver: Any = field(default=_ANY_RECEIVER, repr=False)


@dataclass
class _Target:
    label: str
    code: CodeType
    function: Any = None
    receiver: Any = _ANY_RECEIVER
    native: bool = False


@dataclass
class _Frame:
    key: tuple
    target: int | None
    wall: int = 0
    cpu: int = 0
    child_wall: int = 0
    child_cpu: int = 0


@dataclass
class _Thread:
    ident: int
    native_id: int
    rows: dict = field(default_factory=dict)
    stack: list = field(default_factory=list)
    pending: tuple | None = None
    overflow: int = 0


def _invalid(field_name):
    raise ObservationError("SMONITOR-OBSERVATION-INVALID", extra={"field": field_name})


def _code(target):
    if not isinstance(target, (FunctionType, MethodType, CodeType)):
        _invalid("synchronous_python_target")
    function = target.__func__ if isinstance(target, MethodType) else target
    code = function if isinstance(function, CodeType) else getattr(function, "__code__", None)
    if not isinstance(code, CodeType) or code.co_flags & (
        inspect.CO_GENERATOR | inspect.CO_COROUTINE | inspect.CO_ASYNC_GENERATOR
    ):
        _invalid("synchronous_python_target")
    return code


class CallObservation:
    """One finite selected-call scope. Use ``observe_calls`` to construct it."""

    def __init__(
        self,
        targets: Mapping[str, Any],
        *,
        identity: str = "code",
        threads: str = "current",
        mode: str = "timings",
        tool_id: int = 3,
        max_events: int = 100_000,
        max_threads: int = 64,
        max_depth: int = 128,
    ):
        if identity not in ("code", "callable") or threads not in ("current", "all"):
            _invalid("identity_or_threads")
        if mode not in ("counts", "timings") or type(tool_id) is not int or not 0 <= tool_id <= 5:
            _invalid("mode_or_tool_id")
        for name, value, limit in (
            ("max_events", max_events, 10_000_000),
            ("max_threads", max_threads, 1024),
            ("max_depth", max_depth, 4096),
        ):
            if type(value) is not int or not 1 <= value <= limit:
                _invalid(name)
        if not isinstance(targets, Mapping) or not 1 <= len(targets) <= 64:
            _invalid("targets")
        if max_threads * max_depth > 65536:
            _invalid("stack_budget")
        self._targets = []
        for label, target in targets.items():
            if type(label) is not str or re.fullmatch(r"[A-Za-z0-9_.:-]{1,64}", label) is None:
                _invalid("target_label")
            if isinstance(target, NativeCallTarget):
                if not isinstance(target.function, (BuiltinFunctionType, MethodDescriptorType)):
                    _invalid("native_function")
                function, receiver = target.function, target.receiver
                bound = getattr(function, "__self__", None)
                if bound is not None and not isinstance(bound, ModuleType):
                    if receiver is not _ANY_RECEIVER and receiver is not bound:
                        _invalid("native_receiver")
                    receiver = bound
                    function = inspect.getattr_static(type(bound), function.__name__, None)
                    if not isinstance(function, MethodDescriptorType):
                        _invalid("native_descriptor")
                selected = _Target(label, _code(target.caller), function, receiver, True)
            else:
                if not isinstance(target, (FunctionType, MethodType, CodeType)):
                    _invalid("python_function")
                if identity == "callable" and isinstance(target, CodeType):
                    _invalid("callable_identity")
                function = target.__func__ if isinstance(target, MethodType) else target
                receiver = target.__self__ if isinstance(target, MethodType) else _ANY_RECEIVER
                selected = _Target(label, _code(target), function, receiver)
            for previous in self._targets:
                if selected.native != previous.native or selected.code is not previous.code:
                    continue
                if identity == "code" and not selected.native:
                    _invalid("duplicate_code")
                if selected.function is previous.function and (
                    selected.receiver is previous.receiver
                    or selected.receiver is _ANY_RECEIVER
                    or previous.receiver is _ANY_RECEIVER
                ):
                    _invalid("overlapping_targets")
            self._targets.append(selected)
        self.identity, self.threads, self.mode, self.tool_id = identity, threads, mode, tool_id
        self._max_events, self._max_threads, self._max_depth = max_events, max_threads, max_depth
        self._lock = threading.RLock()
        self._local = threading.local()
        self._states = []
        self._codes = {
            id(target.code): target.code for target in self._targets if not target.native
        }
        self._python = {
            id(target.code): i for i, target in enumerate(self._targets) if not target.native
        }
        self._native = [i for i, target in enumerate(self._targets) if target.native]
        self._metadata = [
            {
                "label": t.label,
                "kind": "native" if t.native else "python",
                "caller_identity": "code" if t.native else None,
            }
            for t in self._targets
        ]
        self._name = f"smonitor.observe_calls.{id(self)}"
        self._started = self._running = self._closed = False
        self._events = self._callbacks = self._dropped = self._errors = self._unmatched = 0
        self._unknown_entries = self._incomplete = 0
        self._callback_errors = 0
        self._registered = []

    def _state(self):
        if not self._running or (
            self.threads == "current" and threading.get_ident() != self._owner
        ):
            return None
        state = getattr(self._local, "state", None)
        if state is None:
            if len(self._states) >= self._max_threads:
                self._dropped += 1
                return None
            state = _Thread(threading.get_ident(), threading.get_native_id())
            self._local.state = state
            self._states.append(state)
        return state

    def _begin(self, state, key, index):
        if (
            self._events >= self._max_events
            or state.overflow
            or len(state.stack) >= self._max_depth
        ):
            state.overflow += 1
            self._dropped += 1
            return
        self._events += 1
        wall = time.perf_counter_ns() if self.mode == "timings" else 0
        cpu = time.thread_time_ns() if self.mode == "timings" else 0
        state.stack.append(_Frame(key, index, wall, cpu))
        if index is not None:
            row = state.rows.setdefault(
                index,
                dict(
                    calls=0,
                    returns=0,
                    unwinds=0,
                    inclusive_wall_ns=0 if self.mode == "timings" else None,
                    selected_exclusive_wall_ns=0 if self.mode == "timings" else None,
                    inclusive_thread_cpu_ns=0 if self.mode == "timings" else None,
                    selected_exclusive_thread_cpu_ns=0 if self.mode == "timings" else None,
                ),
            )
            row["calls"] += 1

    def _end(self, state, key, outcome):
        if state.overflow:
            state.overflow -= 1
            return
        if not state.stack or state.stack[-1].key != key:
            self._unmatched += 1
            return
        frame = state.stack.pop()
        if frame.target is None:
            return
        row = state.rows[frame.target]
        row[outcome] += 1
        if self.mode == "timings":
            wall, cpu = time.perf_counter_ns() - frame.wall, time.thread_time_ns() - frame.cpu
            row["inclusive_wall_ns"] += wall
            row["inclusive_thread_cpu_ns"] += cpu
            row["selected_exclusive_wall_ns"] += max(0, wall - frame.child_wall)
            row["selected_exclusive_thread_cpu_ns"] += max(0, cpu - frame.child_cpu)
            # An ignored alias is transparent to selected-exclusive accounting.
            for parent in reversed(state.stack):
                if parent.target is not None:
                    parent.child_wall += wall
                    parent.child_cpu += cpu
                    break

    def _dispatch(self, operation, *args, **kwargs):
        with self._lock:
            if not self._running:
                return
            self._callbacks += 1
            try:
                operation(*args, **kwargs)
            except Exception:
                self._errors += 1
                self._callback_errors += 1
                self._running = False

    def _call(self, code, offset, function, arg0):
        native = [i for i in self._native if self._targets[i].code is code]
        fn = function.__func__ if isinstance(function, MethodType) else function
        receiver = function.__self__ if isinstance(function, MethodType) else arg0
        fn_code = fn.__code__ if isinstance(fn, FunctionType) else None
        if not native and not (self.identity == "callable" and id(fn_code) in self._codes):
            return
        state = self._state()
        if state is None:
            return
        if self.identity == "callable" and id(fn_code) in self._codes:
            selected = next(
                (
                    i
                    for i, target in enumerate(self._targets)
                    if not target.native
                    and target.function is fn
                    and (target.receiver is _ANY_RECEIVER or target.receiver is receiver)
                ),
                None,
            )
            state.pending = (fn_code, selected)
        for index in native:
            target = self._targets[index]
            if target.function is function and (
                target.receiver is _ANY_RECEIVER or target.receiver is arg0
            ):
                self._begin(state, ("native", id(code), offset), index)

    def _start(self, code, offset):
        state = self._state()
        if state is None:
            return
        index = self._python.get(id(code))
        if self.identity == "callable":
            if state.pending is None or state.pending[0] is not code:
                self._unknown_entries += 1
                index = None
            else:
                index = state.pending[1]
            state.pending = None
        self._begin(state, ("python", id(code)), index)

    def _finish_python(self, code, offset, value, *, outcome):
        if id(code) in self._codes:
            state = self._state()
            if state is not None:
                self._end(state, ("python", id(code)), outcome)

    def _finish_native(self, code, offset, function, arg0, *, outcome):
        if any(
            self._targets[i].code is code
            and self._targets[i].function is function
            and (self._targets[i].receiver is _ANY_RECEIVER or self._targets[i].receiver is arg0)
            for i in self._native
        ):
            state = self._state()
            if state is not None:
                self._end(state, ("native", id(code), offset), outcome)

    def __enter__(self):
        if self._started:
            _invalid("single_use_scope")
        monitoring = getattr(sys, "monitoring", None)
        if (
            sys.implementation.name != "cpython"
            or monitoring is None
            or (hasattr(sys, "_is_gil_enabled") and not sys._is_gil_enabled())
        ):
            raise ObservationError("SMONITOR-OBSERVATION-UNSUPPORTED")
        self._monitoring = monitoring
        if monitoring.get_tool(self.tool_id) is not None or monitoring.get_events(self.tool_id):
            raise ObservationError("SMONITOR-OBSERVATION-CONFLICT")
        self._owner = threading.get_ident()
        self._started = True
        events = monitoring.events
        callbacks = {
            events.PY_START: lambda *a: self._dispatch(self._start, *a),
            events.PY_RETURN: lambda *a: self._dispatch(self._finish_python, *a, outcome="returns"),
            events.PY_UNWIND: lambda *a: self._dispatch(self._finish_python, *a, outcome="unwinds"),
        }
        global_events = events.PY_UNWIND
        if self.identity == "callable" or self._native:
            callbacks[events.CALL] = lambda *a: self._dispatch(self._call, *a)
            global_events |= events.CALL
        if self._native:
            callbacks[events.C_RETURN] = lambda *a: self._dispatch(
                self._finish_native, *a, outcome="returns"
            )
            callbacks[events.C_RAISE] = lambda *a: self._dispatch(
                self._finish_native, *a, outcome="unwinds"
            )
            global_events |= events.C_RETURN | events.C_RAISE
        try:
            monitoring.use_tool_id(self.tool_id, self._name)
        except ValueError:
            self._started = False
            raise ObservationError("SMONITOR-OBSERVATION-CONFLICT") from None
        try:
            for event, callback in callbacks.items():
                monitoring.register_callback(self.tool_id, event, callback)
                self._registered.append(event)
            self._wall_start, self._cpu_start = time.perf_counter_ns(), time.process_time_ns()
            self._gc_start = gc.get_stats()
            self._running = True
            for code in self._codes.values():
                monitoring.set_local_events(self.tool_id, code, events.PY_START | events.PY_RETURN)
            monitoring.set_events(self.tool_id, global_events)
        except BaseException as error:
            self.stop()
            if not isinstance(error, Exception):
                raise
            raise ObservationError(
                "SMONITOR-OBSERVATION-IO", extra={"operation": "tool_setup"}
            ) from None
        return self

    def _release_tool(self):
        monitoring = self._monitoring
        if monitoring.get_tool(self.tool_id) != self._name:
            self._errors += 1
            return False
        actions = [(monitoring.set_events, (self.tool_id, 0))]
        actions.extend(
            (monitoring.set_local_events, (self.tool_id, code, 0)) for code in self._codes.values()
        )
        actions.extend(
            (monitoring.register_callback, (self.tool_id, event, None))
            for event in self._registered
        )
        # Every cleanup boundary is attempted, including after an earlier error.
        for _ in range(2):
            failed = []
            for function, args in actions:
                try:
                    function(*args)
                except Exception:
                    self._errors += 1
                    failed.append((function, args))
            actions = failed
            if not actions:
                try:
                    monitoring.free_tool_id(self.tool_id)
                    return True
                except Exception:
                    self._errors += 1
        return False

    def stop(self):
        with self._lock:
            if not self._started:
                return
            if self._closed:
                if not self._released:
                    self._released = self._release_tool()
                    if self._released:
                        self._codes.clear()
                return
            self._running = False
            self._closed = True
            self._released = self._release_tool()
            try:
                wall, cpu = time.perf_counter_ns(), time.process_time_ns()
                self._wall_ns = wall - getattr(self, "_wall_start", wall)
                self._process_cpu_ns = cpu - getattr(self, "_cpu_start", cpu)
            except Exception:
                self._errors += 1
                self._wall_ns = self._process_cpu_ns = None
            try:
                end_gc = gc.get_stats()
                self._gc_delta = [
                    {
                        key: end.get(key, 0) - start.get(key, 0)
                        for key in ("collections", "collected", "uncollectable")
                    }
                    for start, end in zip(getattr(self, "_gc_start", end_gc), end_gc)
                ]
            except Exception:
                self._errors += 1
                self._gc_delta = None
            for state in self._states:
                self._incomplete += len(state.stack) + state.overflow
                state.stack.clear()
                state.pending = None
            self._targets.clear()
            if self._released:
                self._codes.clear()
            self._python.clear()
            self._native.clear()

    def __exit__(self, *exc):
        self.stop()
        return False

    def report(self):
        """Return bounded primitive aggregates after the scope has closed."""
        if not self._closed:
            _invalid("report_requires_closed_scope")
        with self._lock:
            return deepcopy(
                {
                    "schema": "smonitor.call-observation@1",
                    "backend": "cpython.sys.monitoring",
                    "identity": self.identity,
                    "thread_scope": self.threads,
                    "mode": self.mode,
                    "status": "incomplete"
                    if (
                        self._errors
                        or self._dropped
                        or self._unmatched
                        or self._unknown_entries
                        or self._incomplete
                    )
                    else "observed",
                    "callback_errors": self._callback_errors,
                    "observation_errors": self._errors,
                    "tool_released": self._released,
                    "callbacks": self._callbacks,
                    "dropped_entries": self._dropped,
                    "unmatched_exits": self._unmatched,
                    "unattributed_entries": self._unknown_entries,
                    "open_frames_at_stop": self._incomplete,
                    "scope_wall_ns": self._wall_ns,
                    "scope_process_cpu_ns": self._process_cpu_ns,
                    "gc_counters_delta": self._gc_delta,
                    "gc_elapsed_ns": None,
                    "targets": self._metadata,
                    "threads": [
                        {
                            "sequence": n,
                            "python_thread_id": s.ident,
                            "native_thread_id": s.native_id,
                            "targets": {
                                self._metadata[i]["label"]: row for i, row in s.rows.items()
                            },
                        }
                        for n, s in enumerate(self._states)
                    ],
                }
            )


def observe_calls(targets: Mapping[str, Any], **options) -> CallObservation:
    """Observe selected synchronous calls without replacing their identities.

    CPython 3.12–3.14 with the GIL is supported. Code selection aggregates every
    callable sharing the selected code. Callable selection additionally needs
    Python CALL events. The scope retains no frames, argument/return payloads or
    exception objects. Timings include monitoring overhead.
    """
    return CallObservation(targets, **options)
