from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter
from typing import Any

from .core.manager import get_manager


@contextmanager
def span(name: str, **meta: Any):
    manager = get_manager()
    if not manager.config.profiling:
        yield
        return
    if manager.config.profiling_sample_rate < 1.0:
        from random import random
        if random() > manager.config.profiling_sample_rate:
            yield
            return
    start = perf_counter()
    try:
        yield
    finally:
        duration_ms = (perf_counter() - start) * 1000.0
        manager.record_timing(name, duration_ms, span=True, meta=meta)


def export_timeline(path: str, format: str = "json") -> None:
    import json
    import csv

    manager = get_manager()
    timeline = manager.report().get("timeline", [])
    if format == "json":
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(timeline, fh, ensure_ascii=False, indent=2)
        return
    if format == "csv":
        if not timeline:
            return
        keys = sorted({k for row in timeline for k in row.keys()})
        with open(path, "w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=keys)
            writer.writeheader()
            for row in timeline:
                writer.writerow(row)
        return
    raise ValueError("Unsupported format")
