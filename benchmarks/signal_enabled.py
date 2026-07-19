"""Overhead of a decorated call on the *enabled* path, emitting nothing.

`signal_disabled.py` covers the `enabled=False` fast path. This one covers the
case scientific users actually run in: telemetry on, but the call is quiet — no
event is emitted, so every nanosecond spent is pure overhead.

Nesting is measured too: sibling libraries stack as many as 16 decorated calls
per public operation, so per-call costs that scale with stack depth are paid
many times over.

Results are normalized against a bare call measured in the same process, since
absolute nanoseconds vary widely between hosts.
"""

from __future__ import annotations

import json
from timeit import timeit

import smonitor


def _per_call_ns(fn, number: int) -> float:
    return timeit(lambda: fn(1), number=number) / number * 1e9


def main(number: int = 300_000, nested_depth: int = 16) -> None:
    def plain(value: int) -> int:
        return value + 1

    decorated = smonitor.signal(plain)

    nested = plain
    for _ in range(nested_depth):
        nested = smonitor.signal(nested)

    smonitor.configure(handlers=[], enabled=True)
    bare_ns = _per_call_ns(plain, number)
    enabled_ns = _per_call_ns(decorated, number)
    nested_ns = _per_call_ns(nested, max(number // 15, 1000))

    smonitor.configure(handlers=[], enabled=False)
    disabled_ns = _per_call_ns(decorated, number)

    print(
        json.dumps(
            {
                "calls": number,
                "nested_depth": nested_depth,
                "bare_ns": bare_ns,
                "disabled_ns": disabled_ns,
                "enabled_ns": enabled_ns,
                "nested_enabled_ns": nested_ns,
                "enabled_ratio": enabled_ns / bare_ns,
                "disabled_ratio": disabled_ns / bare_ns,
                "nested_ns_per_wrapper": (nested_ns - bare_ns) / nested_depth,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
