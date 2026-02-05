from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Dict, Optional


def load_config_from_path(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location("_smonitor", str(path))
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data: Dict[str, Any] = {}
    # Load all uppercase symbols to allow validation of unknown keys
    for key in dir(module):
        if key.isupper():
            data[key] = getattr(module, key)
    return data


def discover_config(start: Path) -> Optional[Dict[str, Any]]:
    current = start.resolve()
    for parent in [current, *current.parents]:
        candidate = parent / "_smonitor.py"
        cfg = load_config_from_path(candidate)
        if cfg is not None:
            return cfg
    return None
