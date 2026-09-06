# Example _smonitor.py

PROFILE = "user"

SMONITOR = {
    "level": "WARNING",
    "trace_depth": 3,
    "capture_warnings": True,
    "capture_logging": True,
    "theme": "plain",
    "slow_signal_ms": 0.0,
    "slow_signal_level": "INFO",
    "warning_coalesce_window_s": 0.0,
}

# A profile block overrides the SMONITOR block when that profile is active.
# Its keys are the same keys: the profile *name* already selects the output
# style, so there is nothing else to name here.
PROFILES = {
    "user": {"level": "WARNING"},
    "dev": {"level": "INFO"},
    "qa": {"level": "INFO"},
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
