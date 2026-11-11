"""Catalog for SMonitor's own integration and capture diagnostics."""

CODES = {
    "SMONITOR-OBSERVATION-INVALID": {
        "message": "Observation selection or bounds are invalid.",
        "user_hint": "Use supported targets, explicit scope and positive bounded limits.",
    },
    "SMONITOR-OBSERVATION-UNSUPPORTED": {
        "message": "The requested observation backend is unavailable.",
        "user_hint": "Check the documented interpreter and operating-system capability boundary.",
    },
    "SMONITOR-OBSERVATION-CONFLICT": {
        "message": "Observation resources are already owned or their ownership changed.",
        "user_hint": "Select an unused tool slot or an independent owned process family.",
    },
    "SMONITOR-OBSERVATION-IO": {
        "message": "Observation could not start or finish its bounded resource operation.",
        "user_hint": "Inspect the retained operation and coverage status before retrying.",
    },
    "SMONITOR-CAPTURE-INVALID": {
        "message": "Diagnostic capture policy or safe metadata is invalid.",
        "user_hint": "Use boolean policy fields and at most 32 bounded primitive metadata fields.",
    },
    "SMONITOR-METADATA-ONLY": {
        "message": "Diagnostic details omitted by capture policy.",
    },
    "SMONITOR-NATIVE-FAILURE": {
        "message": "Operation failed; native exception details omitted by capture policy.",
    },
    "SMONITOR-SIGNAL-FALLBACK": {
        "message": "SMonitor signal {stage} failed for {signal}.",
        "dev_message": "SMonitor signal {stage} failed for {signal}: {detail}",
    },
    "SMONITOR-HANDLER-DEGRADED": {
        "message": "Handler '{name}' reached error threshold ({count}/{threshold}) and is considered degraded.",
    },
    "SMONITOR-BUNDLE-SELECTION-INVALID": {
        "message": "Invalid identity bundle selection; use a nonnegative event limit and approved code identifiers.",
    },
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


class ObservationError(ValueError):
    """An observation rejected before changing the caller's execution policy."""

    def __init__(self, code, *, extra=None):
        self.code = code
        self.extra = extra or {}
        entry = CODES[code]
        super().__init__(entry["message"] + " " + entry["user_hint"])


class ProviderRegistrationError(ValueError):
    """Registration rejected before catalog state was changed."""

    def __init__(self, code, *, extra=None):
        self.code = code
        self.extra = extra or {}
        entry = CODES[code]
        super().__init__(entry["message"] + " " + entry["user_hint"])


class CapturePolicyError(ValueError):
    code = "SMONITOR-CAPTURE-INVALID"

    def __init__(self):
        entry = CODES[self.code]
        super().__init__(entry["message"] + " " + entry["user_hint"])
