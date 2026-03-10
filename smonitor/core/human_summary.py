from __future__ import annotations

from typing import Any, Dict, Optional


def build_human_summary(
    *,
    level: Optional[str],
    message: Optional[str],
    code: Optional[str],
    source: Optional[str],
    hint: Optional[str],
    extra: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    extra = extra or {}
    return {
        "level": level,
        "code": code,
        "message": message,
        "source": source,
        "hint": hint,
        "recommended_action": extra.get("recommended_action"),
        "next_step": extra.get("next_step"),
    }
