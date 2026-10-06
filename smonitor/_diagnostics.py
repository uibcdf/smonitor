"""Catalog for SMonitor's own integration and capture diagnostics."""

CODES = {
    "SMONITOR-PROVIDER-INVALID": {
        "message": "Provider diagnostic declarations are invalid.",
        "user_hint": "Validate the provider's CODES and SIGNALS before registration.",
    },
    "SMONITOR-PROVIDER-CONFLICT": {
        "message": "Provider diagnostic declarations conflict with registered definitions.",
        "user_hint": "Use distinct code and signal names or identical shared definitions.",
    },
    "SMONITOR-PROVIDER-IDENTITY": {
        "message": "Provider identity is already registered with different declarations.",
        "user_hint": "Use a unique provider identity and keep its declarations stable.",
    },
}


class ProviderRegistrationError(ValueError):
    """Registration rejected before catalog state was changed."""

    def __init__(self, code, *, extra=None):
        self.code = code
        self.extra = extra or {}
        entry = CODES[code]
        super().__init__(entry["message"] + " " + entry["user_hint"])
