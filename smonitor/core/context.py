from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from contextvars import ContextVar
from typing import Any, Dict, List, Optional


@dataclass
class Frame:
    function: str
    module: str
    args: Optional[Dict[str, Any]] = None
    time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tags: Optional[List[str]] = None
    duration_ms: Optional[float] = None


_context_stack: ContextVar[List[Frame]] = ContextVar("smonitor_context_stack", default=[])


def push_frame(frame: Frame) -> None:
    stack = list(_context_stack.get())
    stack.append(frame)
    _context_stack.set(stack)


def pop_frame() -> Optional[Frame]:
    stack = list(_context_stack.get())
    if not stack:
        return None
    frame = stack.pop()
    _context_stack.set(stack)
    return frame


def get_context(trace_depth: Optional[int] = None) -> Optional[Dict[str, Any]]:
    stack = list(_context_stack.get())
    if not stack:
        return None
    if trace_depth is not None:
        stack = stack[-trace_depth:]
    chain = [f"{f.module}.{f.function}" for f in stack]
    return {
        "chain": chain,
        "depth": len(chain),
        "frames": [frame.__dict__ for frame in stack],
    }
