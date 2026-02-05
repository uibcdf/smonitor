# Example _smonitor.py

PROFILE = "user"

SMONITOR = {
    "level": "WARNING",
    "trace_depth": 3,
    "capture_warnings": True,
    "capture_logging": True,
    "theme": "plain",
}

PROFILES = {
    "user": {"level": "WARNING", "style": "user"},
    "dev": {"level": "INFO", "style": "dev"},
    "qa": {"level": "INFO", "style": "qa"},
}

ROUTES = [
    {"when": {"level": "WARNING"}, "send_to": ["console", "json"]}
]

FILTERS = [
    {"when": {"code": "MSM-W010"}, "rate_limit": "1/100"}
]

CODES = {
    "MSM-W010": {
        "title": "Selection ambiguous",
        "user_message": "La selección '{selection}' es ambigua.",
        "user_hint": "Especifica la selección con más detalle (ejemplo: {example}).",
        "dev_message": "Selection parsing ambiguous.",
        "dev_hint": "Use explicit selectors.",
    }
}

SIGNALS = {
    "molsysmt.select": {
        "warnings": ["MSM-W010"],
        "extra_required": ["selection", "example"],
    }
}
