from __future__ import annotations

from contextvars import ContextVar
from datetime import datetime, timezone
from time import time as _now
from typing import Any, Dict, List, Optional

# A breadcrumb frame is a plain list, and the stack is a linked list threaded
# through the frame's last slot — innermost frame first, `None` at the bottom.
#
# This is the hottest allocation in SMonitor: one per decorated call, built
# whether or not anything is ever emitted. The representation is therefore
# chosen for creation cost. A slotted dataclass cost ~490 ns to build; this
# costs ~170 ns, of which ~80 ns is reading the wall clock. Linking rather than
# copying keeps push/pop O(1) at any nesting depth, which matters because
# sibling libraries stack as many as 16 decorated calls per public operation.
#
# The trade is readability, bought back with named slot constants and the rule
# that nothing outside this module indexes a frame directly. Frames are treated
# as immutable once a child frame is pushed on top: only the owning wrapper
# mutates its own frame, so a child context can never disturb its parent's.
FUNCTION = 0
MODULE = 1
ARGS = 2
TAGS = 3
EXTRA = 4
DURATION_MS = 5
EPOCH = 6
PARENT = 7

#: A breadcrumb frame. Always built by `push_frame`, never constructed directly.
Frame = List[Any]

_context_stack: ContextVar[Optional[Frame]] = ContextVar(
    "smonitor_context_stack", default=None
)


def push_frame(
    function: str,
    module: str,
    *,
    args: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Frame:
    """Push a breadcrumb frame and return it, for later `set_frame_*` calls."""
    frame: Frame = [function, module, args, tags, extra, None, _now(), _context_stack.get()]
    _context_stack.set(frame)
    return frame


def pop_frame() -> Optional[Frame]:
    """Pop the innermost frame, or return `None` if the stack is empty."""
    frame = _context_stack.get()
    if frame is None:
        return None
    _context_stack.set(frame[PARENT])
    return frame


def frame_args(frame: Frame) -> Optional[Dict[str, Any]]:
    return frame[ARGS]


def set_frame_args(frame: Frame, args: Optional[Dict[str, Any]]) -> None:
    """Attach an argument summary, so error events can report the call inputs."""
    frame[ARGS] = args


def set_frame_duration(frame: Frame, duration_ms: float) -> None:
    """Record how long the call took.

    Set before the frame is popped, so a slow-signal event emitted from the
    same `finally` block carries the duration in its context.
    """
    frame[DURATION_MS] = duration_ms


def frame_time(frame: Frame) -> str:
    """ISO-8601 UTC timestamp of when the frame was pushed.

    Rendered here rather than at push time: formatting it eagerly cost more
    than the rest of the wrapper combined, and it is read only on emission.
    """
    return datetime.fromtimestamp(frame[EPOCH], timezone.utc).isoformat()


def frame_as_dict(frame: Frame) -> Dict[str, Any]:
    """Serialize for the event `context.frames` payload."""
    return {
        "function": frame[FUNCTION],
        "module": frame[MODULE],
        "args": frame[ARGS],
        "time": frame_time(frame),
        "tags": frame[TAGS],
        "extra": frame[EXTRA],
        "duration_ms": frame[DURATION_MS],
    }


def get_context(trace_depth: Optional[int] = None) -> Optional[Dict[str, Any]]:
    frame = _context_stack.get()
    if frame is None:
        return None
    # `trace_depth` of 0 or None means "the whole stack", matching the negative
    # slicing this replaced (`stack[-0:]` is the full list).
    limit = trace_depth if trace_depth else None
    stack: List[Frame] = []
    while frame is not None and (limit is None or len(stack) < limit):
        stack.append(frame)
        frame = frame[PARENT]
    # Collected innermost-first; the payload is ordered outermost-first.
    stack.reverse()
    chain = [f"{f[MODULE]}.{f[FUNCTION]}" for f in stack]
    return {
        "chain": chain,
        "depth": len(chain),
        "frames": [frame_as_dict(f) for f in stack],
    }
