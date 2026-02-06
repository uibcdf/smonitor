from __future__ import annotations

import json
import platform
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import smonitor
from smonitor.config import load_project_config
from smonitor.core.manager import get_manager


def _parse_since(since: Optional[str]) -> Optional[datetime]:
    if not since:
        return None
    try:
        return datetime.fromisoformat(since)
    except ValueError:
        return None


def _redact_path(data: Dict[str, Any], path: str) -> None:
    parts = path.split(".")
    current: Any = data
    for part in parts[:-1]:
        if not isinstance(current, dict):
            return
        current = current.get(part)
    if isinstance(current, dict) and parts[-1] in current:
        current[parts[-1]] = "***"


def _sanitize_event(
    event: Dict[str, Any],
    *,
    drop_extra: bool,
    drop_context: bool,
    redact_fields: Iterable[str],
) -> Dict[str, Any]:
    sanitized = dict(event)
    if drop_extra:
        sanitized.pop("extra", None)
    if drop_context:
        sanitized.pop("context", None)
    for field in redact_fields:
        _redact_path(sanitized, field)
    return sanitized


def collect_bundle(
    *,
    project_config: Optional[Dict[str, Any]] = None,
    include_events: bool = True,
    max_events: Optional[int] = None,
    since: Optional[str] = None,
    drop_extra: bool = False,
    drop_context: bool = False,
    redact_fields: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    manager = get_manager()
    cfg = asdict(manager.config)
    report = manager.report()
    since_dt = _parse_since(since)
    redact_fields = redact_fields or []
    events = manager.recent_events(max_events) if include_events else []
    if since_dt:
        filtered = []
        for event in events:
            timestamp = event.get("timestamp")
            try:
                evt_dt = datetime.fromisoformat(timestamp) if isinstance(timestamp, str) else None
            except ValueError:
                evt_dt = None
            if evt_dt and evt_dt >= since_dt:
                filtered.append(event)
        events = filtered
    if include_events:
        events = [
            _sanitize_event(
                event,
                drop_extra=drop_extra,
                drop_context=drop_context,
                redact_fields=redact_fields,
            )
            for event in events
        ]
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
        "redactions": {
            "drop_extra": drop_extra,
            "drop_context": drop_context,
            "redact_fields": list(redact_fields),
            "since": since,
        },
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
    since: Optional[str] = None,
    drop_extra: bool = False,
    drop_context: bool = False,
    redact_fields: Optional[Iterable[str]] = None,
    force: bool = False,
    append_events: bool = False,
) -> Path:
    path = Path(path)
    if path.suffix in {".json", ".jsonl"}:
        if path.exists() and not force:
            raise FileExistsError(f"{path} already exists")
        bundle = collect_bundle(
            project_config=project_config,
            include_events=include_events,
            max_events=max_events,
            since=since,
            drop_extra=drop_extra,
            drop_context=drop_context,
            redact_fields=redact_fields,
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists")
    path.mkdir(parents=True, exist_ok=True)
    bundle = collect_bundle(
        project_config=project_config,
        include_events=False,
        max_events=max_events,
        since=since,
        drop_extra=drop_extra,
        drop_context=drop_context,
        redact_fields=redact_fields,
    )
    bundle_path = path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    if include_events:
        events = collect_bundle(
            project_config=project_config,
            include_events=True,
            max_events=max_events,
            since=since,
            drop_extra=drop_extra,
            drop_context=drop_context,
            redact_fields=redact_fields,
        )["events"]
        events_path = path / "events.jsonl"
        mode = "a" if append_events else "w"
        with events_path.open(mode, encoding="utf-8") as fh:
            for event in events:
                fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    return path


def export_bundle(
    path: str | Path,
    *,
    include_events: bool = True,
    max_events: Optional[int] = None,
    since: Optional[str] = None,
    drop_extra: bool = False,
    drop_context: bool = False,
    redact_fields: Optional[Iterable[str]] = None,
    force: bool = False,
    append_events: bool = False,
    config_base: Optional[Path] = None,
) -> Path:
    project_config = load_project_config(config_base or Path.cwd())
    return write_bundle(
        Path(path),
        project_config=project_config,
        include_events=include_events,
        max_events=max_events,
        since=since,
        drop_extra=drop_extra,
        drop_context=drop_context,
        redact_fields=redact_fields,
        force=force,
        append_events=append_events,
    )
