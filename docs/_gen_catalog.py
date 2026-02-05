from pathlib import Path
import smonitor
from smonitor.config import load_project_config
from smonitor.docs_utils import render_codes_table, render_signals_table

root = Path(__file__).resolve().parents[1]

cfg = load_project_config(root) or {}

codes_md = render_codes_table(cfg.get("CODES", {}))
signals_md = render_signals_table(cfg.get("SIGNALS", {}))

(Path(__file__).parent / "_generated_codes.md").write_text(codes_md, encoding="utf-8")
(Path(__file__).parent / "_generated_signals.md").write_text(signals_md, encoding="utf-8")
