from __future__ import annotations

import json
from timeit import timeit

import smonitor


def main(number: int = 1_000_000) -> None:
    def plain(value: int) -> int:
        return value + 1

    decorated = smonitor.signal(plain)
    smonitor.configure(enabled=False, handlers=[])

    plain_seconds = timeit(lambda: plain(1), number=number)
    disabled_seconds = timeit(lambda: decorated(1), number=number)
    print(
        json.dumps(
            {
                "calls": number,
                "plain_ns": plain_seconds / number * 1e9,
                "disabled_ns": disabled_seconds / number * 1e9,
                "overhead_ns": (disabled_seconds - plain_seconds) / number * 1e9,
                "ratio": disabled_seconds / plain_seconds,
            }
        )
    )


if __name__ == "__main__":
    main()
