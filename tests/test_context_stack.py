"""Contract tests for the breadcrumb stack in `smonitor.core.context`.

The stack is an immutable linked list held in a `ContextVar`, chosen so that
push/pop stay O(1) at any nesting depth. These tests pin the behaviour that
representation must preserve: ordering, `trace_depth` slicing, and isolation
between asyncio tasks, threads, and copied contexts.
"""

from __future__ import annotations

import asyncio
import contextvars
import threading

from smonitor.core.context import Frame, get_context, pop_frame, push_frame


def _push(name: str, module: str = "pkg.mod") -> Frame:
    frame = Frame(function=name, module=module)
    push_frame(frame)
    return frame


def test_empty_stack_has_no_context():
    assert get_context() is None


def test_chain_is_ordered_outermost_first():
    _push("outer")
    _push("middle")
    _push("inner")
    context = get_context()
    assert context["chain"] == ["pkg.mod.outer", "pkg.mod.middle", "pkg.mod.inner"]
    assert context["depth"] == 3
    assert [f["function"] for f in context["frames"]] == ["outer", "middle", "inner"]


def test_trace_depth_keeps_the_innermost_frames():
    _push("a")
    _push("b")
    _push("c")
    context = get_context(2)
    assert context["chain"] == ["pkg.mod.b", "pkg.mod.c"]
    assert context["depth"] == 2


def test_trace_depth_beyond_stack_returns_whole_stack():
    _push("only")
    assert get_context(10)["chain"] == ["pkg.mod.only"]


def test_trace_depth_zero_returns_whole_stack():
    """Matches the negative slicing this replaced: `stack[-0:]` is everything."""
    _push("a")
    _push("b")
    assert get_context(0)["depth"] == 2


def test_pop_returns_frames_in_reverse_order():
    first = _push("a")
    second = _push("b")
    assert pop_frame() is second
    assert pop_frame() is first
    assert pop_frame() is None
    assert get_context() is None


def test_pop_on_empty_stack_is_safe():
    assert pop_frame() is None
    assert pop_frame() is None


def test_copied_context_cannot_disturb_its_parent():
    _push("parent")

    def child() -> None:
        _push("child")
        assert get_context()["depth"] == 2

    contextvars.copy_context().run(child)

    context = get_context()
    assert context["chain"] == ["pkg.mod.parent"]
    assert context["depth"] == 1


def test_threads_do_not_share_frames():
    _push("main")
    seen: dict[str, list[str]] = {}
    barrier = threading.Barrier(3)

    def worker(name: str) -> None:
        _push(name)
        barrier.wait()  # hold both frames live at once
        seen[name] = get_context()["chain"]

    threads = [threading.Thread(target=worker, args=(name,)) for name in ("t1", "t2")]
    for thread in threads:
        thread.start()
    barrier.wait()
    for thread in threads:
        thread.join()

    # Each thread starts from an empty context and sees only its own frame.
    assert seen["t1"] == ["pkg.mod.t1"]
    assert seen["t2"] == ["pkg.mod.t2"]
    assert get_context()["chain"] == ["pkg.mod.main"]


def test_async_tasks_do_not_leak_frames_between_each_other():
    async def task(name: str, chains: dict[str, list[str]]) -> None:
        _push(name)
        await asyncio.sleep(0)  # force interleaving
        chains[name] = get_context()["chain"]

    async def main() -> dict[str, list[str]]:
        chains: dict[str, list[str]] = {}
        await asyncio.gather(task("a", chains), task("b", chains))
        return chains

    chains = asyncio.run(main())
    assert chains["a"] == ["pkg.mod.a"]
    assert chains["b"] == ["pkg.mod.b"]


def test_deep_nesting_preserves_order():
    for index in range(50):
        _push(f"f{index}")
    chain = get_context()["chain"]
    assert chain[0] == "pkg.mod.f0"
    assert chain[-1] == "pkg.mod.f49"
    assert len(chain) == 50
