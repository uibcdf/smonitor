import gc
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from smonitor.profiling import NativeCallTarget, ObservationError, observe_calls

supported = pytest.mark.skipif(not hasattr(sys, "monitoring"), reason="CPython 3.12+ capability")


def rows(report, label):
    return [thread["targets"][label] for thread in report["threads"] if label in thread["targets"]]


@supported
def test_selected_calls_preserve_identity_hooks_gc_and_original_exception():
    error = RuntimeError("private exception value")

    def leaf(fail=False):
        if fail:
            raise error
        return 17

    def outer(fail=False):
        return leaf(fail)

    original_code = leaf.__code__
    profile, trace = sys.getprofile(), sys.gettrace()
    gc_callbacks, enabled, thresholds, flags = (
        gc.callbacks[:],
        gc.isenabled(),
        gc.get_threshold(),
        gc.get_debug(),
    )
    with observe_calls({"outer": outer, "leaf": leaf}) as observation:
        assert outer() == 17
        with pytest.raises(RuntimeError) as caught:
            outer(True)
        assert caught.value is error
    report = observation.report()
    assert leaf.__code__ is original_code
    assert (sys.getprofile(), sys.gettrace()) == (profile, trace)
    assert (gc.callbacks, gc.isenabled(), gc.get_threshold(), gc.get_debug()) == (
        gc_callbacks,
        enabled,
        thresholds,
        flags,
    )
    assert report["status"] == "observed"
    for label in ("outer", "leaf"):
        row = rows(report, label)[0]
        assert (row["calls"], row["returns"], row["unwinds"]) == (2, 1, 1)
        assert row["inclusive_wall_ns"] >= row["selected_exclusive_wall_ns"] >= 0
        assert row["inclusive_thread_cpu_ns"] >= row["selected_exclusive_thread_cpu_ns"] >= 0
    assert report["gc_elapsed_ns"] is None
    assert "private exception" not in json.dumps(report)
    assert sys.monitoring.get_tool(3) is None
    assert sys.monitoring.get_local_events(3, original_code) == 0


@supported
def test_code_aggregation_and_callable_identity_are_distinct():
    def factory(value):
        def work():
            return value

        return work

    one, two = factory(1), factory(2)
    assert one.__code__ is two.__code__
    with observe_calls({"shared_code": one}, mode="counts") as aggregate:
        assert one() == 1
        assert two() == 2
    assert rows(aggregate.report(), "shared_code")[0]["calls"] == 2
    with observe_calls({"one": one, "two": two}, identity="callable") as exact:
        one()
        two()
        one()
    report = exact.report()
    assert report["status"] == "observed"
    assert rows(report, "one")[0]["calls"] == 2
    assert rows(report, "two")[0]["calls"] == 1
    assert aggregate.report()["mode"] == "counts"
    assert rows(aggregate.report(), "shared_code")[0]["inclusive_thread_cpu_ns"] is None


@supported
def test_callable_alias_exclusion_keeps_recursive_stack_balanced():
    def factory():
        def work(next_call=None):
            if next_call:
                next_call()

        return work

    selected, other = factory(), factory()
    with observe_calls({"chosen": selected}, identity="callable") as observation:
        selected(other)
        other()
        selected()
    assert observation.report()["status"] == "observed"
    assert rows(observation.report(), "chosen")[0]["calls"] == 2


@supported
def test_bound_method_identity_selects_the_receiver():
    class Worker:
        def run(self):
            return 1

    chosen, other = Worker(), Worker()
    with observe_calls({"chosen": chosen.run}, identity="callable") as observation:
        chosen.run()
        other.run()
    assert observation.report()["status"] == "observed"
    assert rows(observation.report(), "chosen")[0]["calls"] == 1


@supported
def test_native_target_selects_caller_receiver_and_return_or_raise():
    chosen, other = [1], [2]

    def run(values):
        return values.pop()

    with observe_calls({"pop": NativeCallTarget(run, list.pop, chosen)}) as observation:
        assert run(chosen) == 1
        assert run(other) == 2
        with pytest.raises(IndexError):
            run(chosen)
    report = observation.report()
    assert report["status"] == "observed"
    row = rows(report, "pop")[0]
    assert (row["calls"], row["returns"], row["unwinds"]) == (2, 1, 1)


@supported
@pytest.mark.parametrize("scope,expected", [("current", 1), ("all", 3)])
def test_current_and_all_thread_scopes(scope, expected):
    entered, release = threading.Event(), threading.Event()

    def target(wait=False):
        if wait:
            entered.set()
            assert release.wait(3)
        return 17

    # Existing worker and future worker must both be observed in all-thread mode.
    with ThreadPoolExecutor(max_workers=1) as executor:
        assert executor.submit(lambda: None).result() is None
        with observe_calls({"work": target}, threads=scope) as observation:
            future = executor.submit(target, True)
            assert entered.wait(3)
            thread = threading.Thread(target=target)
            thread.start()
            assert target() == 17
            release.set()
            thread.join(3)
            assert not thread.is_alive()
            assert future.result(timeout=3) == 17
    report = observation.report()
    assert report["status"] == "observed"
    assert sum(row["calls"] for row in rows(report, "work")) == expected


@supported
def test_recursion_and_bounds_report_incomplete_observation():
    def recursive(n):
        return recursive(n - 1) if n else 17

    with observe_calls({"recursive": recursive}, max_depth=2) as observation:
        assert recursive(5) == 17
    report = observation.report()
    assert report["status"] == "incomplete"
    assert report["dropped_entries"] == 4
    assert report["open_frames_at_stop"] == 0
    assert rows(report, "recursive")[0]["returns"] == 2


@supported
def test_owned_tool_conflict_and_nested_independent_scopes():
    def work():
        return 1

    sys.monitoring.use_tool_id(3, "application-owned")
    try:
        with pytest.raises(ObservationError, match="already owned"):
            with observe_calls({"work": work}):
                pytest.fail("conflicting scope entered")
        assert sys.monitoring.get_tool(3) == "application-owned"
    finally:
        sys.monitoring.free_tool_id(3)
    with observe_calls({"outer": work}, tool_id=3) as outer:
        with observe_calls({"inner": work}, tool_id=4) as inner:
            work()
        work()
    assert rows(outer.report(), "outer")[0]["calls"] == 2
    assert rows(inner.report(), "inner")[0]["calls"] == 1


@supported
def test_callback_failure_preserves_work_and_reports_incomplete(monkeypatch):
    def work():
        return 17

    def broken_clock():
        raise RuntimeError("clock failed")

    with observe_calls({"work": work}) as observation:
        with monkeypatch.context() as patch:
            patch.setattr("smonitor._call_observation.time.thread_time_ns", broken_clock)
            assert work() == 17
    assert observation.report()["status"] == "incomplete"
    assert observation.report()["callback_errors"] == 1
    assert sys.monitoring.get_tool(3) is None


def test_unsupported_backend_refuses_without_a_profile_fallback(monkeypatch):
    def work():
        pass

    original = sys.getprofile()
    monkeypatch.delattr(sys, "monitoring", raising=False)
    with pytest.raises(ObservationError) as caught:
        with observe_calls({"work": work}):
            pass
    assert caught.value.code == "SMONITOR-OBSERVATION-UNSUPPORTED"
    assert sys.getprofile() is original


@pytest.mark.parametrize(
    "options", [{"max_depth": 0}, {"max_threads": True}, {"threads": "future"}]
)
def test_invalid_bounds_are_catalog_driven(options):
    with pytest.raises(ObservationError) as caught:
        observe_calls({"work": lambda: None}, **options)
    assert caught.value.code == "SMONITOR-OBSERVATION-INVALID"


@supported
def test_event_replay_has_known_inclusive_and_selected_exclusive_clocks(monkeypatch):
    """The event state machine has an exact independent timing oracle.

    sys.monitoring callbacks cannot themselves be monitored by another tool,
    including coverage's monitoring backend. Direct replay also exercises their
    normal Python entry independently of interpreter callback delivery.
    """

    def outer():
        pass

    def inner():
        pass

    with observe_calls({"outer": outer, "inner": inner}) as observation:
        with monkeypatch.context() as patch:
            wall = iter((0, 10, 30, 50))
            cpu = iter((0, 5, 15, 25))
            patch.setattr("smonitor._call_observation.time.perf_counter_ns", lambda: next(wall))
            patch.setattr("smonitor._call_observation.time.thread_time_ns", lambda: next(cpu))
            observation._dispatch(observation._start, outer.__code__, 0)
            observation._dispatch(observation._start, inner.__code__, 0)
            observation._dispatch(
                observation._finish_python, inner.__code__, 0, None, outcome="returns"
            )
            observation._dispatch(
                observation._finish_python, outer.__code__, 0, None, outcome="unwinds"
            )
    report = observation.report()
    assert report["status"] == "observed"
    outer_row, inner_row = rows(report, "outer")[0], rows(report, "inner")[0]
    assert outer_row["inclusive_wall_ns"] == 50
    assert outer_row["selected_exclusive_wall_ns"] == 30
    assert outer_row["inclusive_thread_cpu_ns"] == 25
    assert outer_row["selected_exclusive_thread_cpu_ns"] == 15
    assert inner_row["inclusive_wall_ns"] == 20


@supported
def test_event_replay_disambiguates_aliases_and_native_receiver():
    def factory():
        return lambda: None

    one, two = factory(), factory()
    items = [1]

    def native_caller():
        pass

    with observe_calls(
        {"one": one, "pop": NativeCallTarget(native_caller, items.pop)},
        identity="callable",
        mode="counts",
    ) as observation:
        for target in (one, two):
            observation._call(native_caller.__code__, 0, target, sys.monitoring.MISSING)
            observation._start(target.__code__, 0)
            observation._finish_python(target.__code__, 0, None, outcome="returns")
        observation._call(native_caller.__code__, 2, list.pop, items)
        observation._finish_native(native_caller.__code__, 2, list.pop, items, outcome="returns")
    report = observation.report()
    assert report["status"] == "observed"
    assert rows(report, "one")[0]["calls"] == 1
    assert rows(report, "pop")[0]["returns"] == 1


@supported
def test_event_limits_and_unattributed_unmatched_entries_are_visible():
    def work():
        pass

    with observe_calls({"work": work}, max_events=1, mode="counts") as observation:
        for _ in range(2):
            observation._start(work.__code__, 0)
            observation._finish_python(work.__code__, 0, None, outcome="returns")
        observation._finish_python(work.__code__, 0, None, outcome="unwinds")
    report = observation.report()
    assert report["dropped_entries"] == 1
    assert report["unmatched_exits"] == 1
    assert report["status"] == "incomplete"
    with observe_calls({"work": work}, identity="callable") as unknown:
        unknown._start(work.__code__, 0)
        unknown._finish_python(work.__code__, 0, None, outcome="returns")
    assert unknown.report()["unattributed_entries"] == 1


@supported
def test_already_active_entry_and_thread_bound_remain_incomplete():
    def work():
        pass

    with observe_calls({"work": work}, threads="all", max_threads=1, mode="counts") as observation:
        observation._start(work.__code__, 0)
        thread = threading.Thread(target=lambda: observation._start(work.__code__, 0))
        thread.start()
        thread.join(3)
    report = observation.report()
    assert report["open_frames_at_stop"] == 1
    assert report["dropped_entries"] == 1
    observation.stop()
    with pytest.raises(ObservationError):
        observation.__enter__()


@supported
def test_separate_equal_code_objects_are_selected_by_identity():
    from types import FunctionType

    first = compile("pass", "same", "exec")
    second = compile("pass", "same", "exec")
    assert first == second and first is not second
    one, two = FunctionType(first, {}), FunctionType(second, {})
    with observe_calls({"one": one, "two": two}) as observation:
        one()
        two()
        two()
    report = observation.report()
    assert rows(report, "one")[0]["calls"] == 1
    assert rows(report, "two")[0]["calls"] == 2


@pytest.mark.parametrize(
    "targets,options",
    [
        ({}, {}),
        ({"unsafe label": lambda: None}, {}),
        ({"work": object()}, {}),
        ({"work": (lambda: None).__code__}, {"identity": "callable"}),
        ({"work": lambda: None}, {"mode": "invalid"}),
        ({"work": NativeCallTarget(lambda: None, lambda: None)}, {}),
        ({"work": NativeCallTarget(object(), len)}, {}),
    ],
)
def test_unsupported_target_forms_are_rejected(targets, options):
    with pytest.raises(ObservationError):
        observe_calls(targets, **options)


@supported
def test_tool_cleanup_retries_transient_failure_and_preserves_native_error(monkeypatch):
    original = sys.monitoring.set_events
    error = RuntimeError("original")
    failed = False

    def flaky(tool, events):
        nonlocal failed
        if events == 0 and not failed:
            failed = True
            raise RuntimeError("cleanup")
        return original(tool, events)

    with pytest.raises(RuntimeError) as caught:
        with observe_calls({"work": lambda: None}) as observation:
            monkeypatch.setattr(sys.monitoring, "set_events", flaky)
            raise error
    assert caught.value is error
    assert observation.report()["tool_released"]
    assert observation.report()["status"] == "incomplete"
    assert sys.monitoring.get_tool(3) is None


@supported
def test_tool_setup_failure_rolls_back_owned_events(monkeypatch):
    original = sys.monitoring.set_local_events

    def fail_start(tool, code, events):
        if events:
            raise RuntimeError("backend error")
        return original(tool, code, events)

    monkeypatch.setattr(sys.monitoring, "set_local_events", fail_start)
    with pytest.raises(ObservationError) as caught:
        with observe_calls({"work": lambda: None}):
            pass
    assert caught.value.code == "SMONITOR-OBSERVATION-IO"
    assert sys.monitoring.get_tool(3) is None


@supported
def test_unsupported_generators_duplicate_selections_and_receiver_conflicts():
    def generator():
        yield 1

    def work():
        pass

    items = []
    for targets in (
        {"generator": generator},
        {"one": work, "two": work},
        {"bound": NativeCallTarget(work, items.pop, [])},
        {"bound": NativeCallTarget(work, dict.fromkeys)},
    ):
        with pytest.raises(ObservationError):
            observe_calls(targets)
    with pytest.raises(ObservationError):
        observe_calls({"work": work}, max_threads=1024, max_depth=1024)
    observation = observe_calls({"work": work})
    observation.stop()
    with pytest.raises(ObservationError):
        observation.report()


@supported
def test_duplicate_callable_target_refused_even_with_alias_code_selection():
    def work():
        pass

    with pytest.raises(ObservationError):
        observe_calls({"one": work, "two": work}, identity="callable")


@supported
def test_final_clock_failure_keeps_body_exception_and_unavailable_clocks(monkeypatch):
    error = RuntimeError("original body exception")

    def broken():
        raise OSError("clock")

    with pytest.raises(RuntimeError) as caught:
        with observe_calls({"work": lambda: None}) as observation:
            monkeypatch.setattr("smonitor._call_observation.time.perf_counter_ns", broken)
            raise error
    assert caught.value is error
    assert observation.report()["scope_wall_ns"] is None
    assert observation.report()["tool_released"]
