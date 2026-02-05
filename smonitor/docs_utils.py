from __future__ import annotations

from typing import Dict


def render_codes_table(codes: Dict[str, dict]) -> str:
    lines = ["Code | Title | User Message", "--- | --- | ---"]
    for code, meta in sorted(codes.items()):
        title = meta.get("title", "")
        user_msg = meta.get("user_message", "")
        lines.append(f"{code} | {title} | {user_msg}")
    return "\n".join(lines)


def render_signals_table(signals: Dict[str, dict]) -> str:
    lines = ["Function | Warnings | Errors | Extra Required", "--- | --- | --- | ---"]
    for fn, meta in sorted(signals.items()):
        warnings = ",".join(meta.get("warnings", []) or [])
        errors = ",".join(meta.get("errors", []) or [])
        extra = ",".join(meta.get("extra_required", []) or [])
        lines.append(f"{fn} | {warnings} | {errors} | {extra}")
    return "\n".join(lines)
