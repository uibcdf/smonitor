from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import time as _now
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class Frame:
    """One entry of the breadcrumb stack pushed by `@signal`.

    A frame is constructed on every decorated call but is only ever read when
    an event is emitted, so the push-time cost is kept minimal: the timestamp
    is stored as an epoch float and rendered to ISO-8601 only by `as_dict()`.
    Formatting it eagerly cost more than the rest of the wrapper combined.
    """

    function: str
    module: str
    args: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    extra: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    epoch: float = field(default_factory=_now)

    @property
    def time(self) -> str:
        """ISO-8601 UTC timestamp of when this frame was pushed."""
        return datetime.fromtimestamp(self.epoch, timezone.utc).isoformat()

    def as_dict(self) -> Dict[str, Any]:
        """Serialize for the event `context.frames` payload."""
        return {
            "function": self.function,
            "module": self.module,
            "args": self.args,
            "time": self.time,
            "tags": self.tags,
            "extra": self.extra,
            "duration_ms": self.duration_ms,
        }


# The stack is an immutable singly-linked list: each node is `(frame, parent)`,
# innermost first, and the innermost node is what the ContextVar holds.
#
# Copying a list on every push/pop — the obvious alternative — is what keeps
# frames from leaking between contexts, but it costs O(depth) per decorated
# call, twice. That matters here: sibling libraries nest as many as 16
# decorated calls per public operation. Consing is O(1) at any depth and is
# immutable, so a child context still cannot disturb its parent. It also lets
# the default be `None` rather than a shared mutable list.
_Node = Optional[tuple]

_context_stack: ContextVar[_Node] = ContextVar("smonitor_context_stack", default=None)


def push_frame(frame: Frame) -> None:
    _context_stack.set((frame, _context_stack.get()))


def pop_frame() -> Optional[Frame]:
    node = _context_stack.get()
    if node is None:
        return None
    _context_stack.set(node[1])
    return node[0]


def get_context(trace_depth: Optional[int] = None) -> Optional[Dict[str, Any]]:
    node = _context_stack.get()
    if node is None:
        return None
    # `trace_depth` of 0 or None means "the whole stack", matching the negative
    # slicing this replaced (`stack[-0:]` is the full list).
    limit = trace_depth if trace_depth else None
    stack: List[Frame] = []
    while node is not None and (limit is None or len(stack) < limit):
        stack.append(node[0])
        node = node[1]
    # Collected innermost-first; the payload is ordered outermost-first.
    stack.reverse()
    chain = [f"{f.module}.{f.function}" for f in stack]
    return {
        "chain": chain,
        "depth": len(chain),
        "frames": [frame.as_dict() for frame in stack],
    }
