"""Declaration-only bundles preserve application policy during real emission."""

import logging
import warnings

import pytest

import smonitor
from smonitor.handlers.memory import MemoryHandler
from smonitor.integrations import DiagnosticBundle


def provider(tmp_path):
    root = tmp_path / "provider"
    root.mkdir()
    root.joinpath("_smonitor.py").write_text(
        'CODES = {"DECL-W001": {"user_message": "Declared warning"},'
        ' "DECL-I001": {"user_message": "Declared info"}}\n'
        'SMONITOR = {"level": "DEBUG", "capture_logging": True,'
        ' "capture_warnings": False}\n'
    )
    return root


@pytest.mark.parametrize("configured", [False, True])
def test_declaration_only_bundle_keeps_config_hooks_handlers_and_scope(tmp_path, configured):
    handler = MemoryHandler()
    if configured:
        smonitor.configure(
            level="DEBUG",
            handlers=[handler],
            capture_logging=False,
            capture_warnings=False,
        )
    manager = smonitor.get_manager()
    previous = manager.config
    hook = warnings.showwarning
    logging_handlers = tuple(logging.getLogger().handlers)
    own_handlers = list(manager._handlers)
    catalog = {
        "warnings": {
            "UserWarning": {"code": "DECL-W001", "level": "WARNING"},
            "SupportTier2Warning": {"code": "DECL-W001", "level": "WARNING"},
        },
        "info": {
            "Ready": {"code": "DECL-I001", "level": "INFO"},
            "SupportTier3Info": {"code": "DECL-I001", "level": "INFO"},
        },
    }
    with smonitor.diagnostic_scope(safe_extra={"operation": "declare"}):
        policy = smonitor.get_capture_policy()
        bundle = DiagnosticBundle(catalog, {}, provider(tmp_path), bootstrap_policy=False)
        assert manager.config is previous
        assert smonitor.resolve(code="DECL-W001")[0] == "Declared warning"
        with pytest.warns(UserWarning) as recorded:
            bundle.warn("first", UserWarning)
            bundle.warn_once("once", UserWarning)
            bundle.warn_once("once", UserWarning)
        assert len(recorded) == 2
        bundle.info("Ready")
        tiers = bundle.tier_registry()
        tiers.register_many({"best_effort": 2, "experimental": 3})
        tiers.check("best_effort")
        tiers.check("experimental")
        assert smonitor.get_capture_policy() == policy
    assert manager.config is previous
    assert warnings.showwarning is hook
    assert tuple(logging.getLogger().handlers) == logging_handlers
    assert manager._handlers == own_handlers
    assert manager._policy_configured == configured
    if configured:
        codes = {event.get("code") for event in handler.events}
        assert codes == {"DECL-W001", "DECL-I001"}


def test_existing_bundle_default_still_bootstraps(tmp_path):
    manager = smonitor.get_manager()
    previous = manager.config
    bundle = DiagnosticBundle(
        {"warnings": {"UserWarning": {"code": "DECL-W001", "level": "WARNING"}}},
        {},
        provider(tmp_path),
    )
    assert manager.config is previous
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        bundle.warn("bootstrap", UserWarning)
    assert manager.config is not previous
    assert manager._policy_configured
    with pytest.warns(UserWarning):
        bundle.warn("normal", UserWarning)
