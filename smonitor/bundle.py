from __future__ import annotations

import json
import platform
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import smonitor
from smonitor.config import load_project_config
from smonitor.core.manager import get_manager


def collect_bundle(
    *,
    project_config: Optional[Dict[str, Any]] = None,
    include_events: bool = True,
    max_events: Optional[int] = None,
) -> Dict[str, Any]:
    manager = get_manager()
    cfg = asdict(manager.config)
    report = manager.report()
    events = manager.recent_events(max_events) if include_events else []
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "smonitor_version": getattr(smonitor, "__version__", "0.0.0+unknown"),
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "argv": list(sys.argv),
        "config": cfg,
        "policy": {
            "routes": manager._policy.get_routes(),
            "filters": manager._policy.get_filters(),
        },
        "codes": manager.get_codes(),
        "signals": manager.get_signals(),
        "report": report,
        "events": events,
    }
    if project_config is not None:
        data["project_config"] = project_config
    return data


def write_bundle(
    path: Path,
    *,
    project_config: Optional[Dict[str, Any]] = None,
    include_events: bool = True,
    max_events: Optional[int] = None,
    force: bool = False,
) -> Path:
    path = Path(path)
    if path.suffix in {".json", ".jsonl"}:
        if path.exists() and not force:
            raise FileExistsError(f"{path} already exists")
        bundle = collect_bundle(project_config=project_config, include_events=include_events, max_events=max_events)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists")
    path.mkdir(parents=True, exist_ok=True)
    bundle = collect_bundle(project_config=project_config, include_events=False, max_events=max_events)
    bundle_path = path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    if include_events:
        events = collect_bundle(project_config=project_config, include_events=True, max_events=max_events)["events"]
        events_path = path / "events.jsonl"
        with events_path.open("w", encoding="utf-8") as fh:
            for event in events:
                fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    return path


def export_bundle(
    path: str | Path,
    *,
    include_events: bool = True,
    max_events: Optional[int] = None,
    force: bool = False,
    config_base: Optional[Path] = None,
) -> Path:
    project_config = load_project_config(config_base or Path.cwd())
    return write_bundle(
        Path(path),
        project_config=project_config,
        include_events=include_events,
        max_events=max_events,
        force=force,
    )
