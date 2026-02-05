from __future__ import annotations

from pathlib import Path
from typing import Dict

from .config import load_project_config
from .docs_utils import render_codes_table, render_signals_table


def generate_catalog(root: Path) -> Dict[str, str]:
    cfg = load_project_config(root) or {}
    return {
        "codes": render_codes_table(cfg.get("CODES", {})),
        "signals": render_signals_table(cfg.get("SIGNALS", {})),
    }


def write_catalog(root: Path, out_dir: Path) -> None:
    data = generate_catalog(root)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "_generated_codes.md").write_text(data["codes"], encoding="utf-8")
    (out_dir / "_generated_signals.md").write_text(data["signals"], encoding="utf-8")
