from concurrent.futures import ThreadPoolExecutor
from itertools import permutations

import pytest

import smonitor
from smonitor.handlers.memory import MemoryHandler
from smonitor.integrations import ProviderRegistrationError, ensure_configured, register_provider


def package(tmp_path, name, *, codes=None, signals=None, policy=True):
    root = tmp_path / name
    root.mkdir()
    root.joinpath("_smonitor.py").write_text(
        f"CODES = {codes or {name: {'message': name, 'agent_message': 'machine'}}!r}\n"
        f"SIGNALS = {signals or {name: {'extra_required': ['operation_id']}}!r}\n"
        + (
            'SMONITOR = {"level": "WARNING", "capture_warnings": True}\nPROFILE = "user"\n'
            if policy
            else ""
        )
    )
    return root


@pytest.mark.parametrize("order", list(permutations(("a", "b", "c"))))
def test_provider_import_preserves_application_policy(tmp_path, order):
    handler = MemoryHandler()
    manager = smonitor.configure(
        level="CRITICAL",
        profile="qa",
        args_summary=False,
        capture_logging=False,
        capture_warnings=False,
        handlers=[handler],
        run_id="application-run",
        session_id="application-session",
        correlation_id="application-op",
        routes=[{"source": "application", "handlers": ["memory"]}],
        filters=[],
    )
    config, policy = manager.config, manager._policy
    roots = {name: package(tmp_path, name) for name in order}
    for name in (*order, *reversed(order)):
        ensure_configured(roots[name])
    assert manager.config is config
    assert manager._policy is policy
    assert manager._handlers == [handler]
    assert manager._run_id == "application-run"
    assert manager._session_id == "application-session"
    assert manager._default_correlation_id == "application-op"
    assert set(manager.get_codes()) == set(order)
    assert set(manager.get_signals()) == set(order)
    assert len(manager.get_providers()) == 3
    bundle = smonitor.collect_bundle()
    assert len(bundle["providers"]) == 3
    assert set(bundle["codes"]) == set(order)


def test_registration_does_not_bootstrap_and_explicit_render_is_pure(tmp_path):
    manager = smonitor.get_manager()
    config = manager.config
    result = register_provider(package(tmp_path, "a"), provider="a")
    assert result["recommendations"]["PROFILE"] == "user"
    assert manager._handlers == []
    assert manager.config is config
    assert not manager._policy_configured
    assert smonitor.resolve(code="a", profile="agent") == ("machine", None)
    assert manager.config is config
    assert manager._handlers == []
    result["codes"]["a"]["message"] = "changed"
    snapshot = manager.get_providers()
    snapshot["a"]["codes"]["a"]["message"] = "changed"
    assert smonitor.resolve(code="a")[0] == "a"


def test_first_bootstrap_and_explicit_policy_opt_in(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    root = package(tmp_path, "a")
    ensure_configured(root)
    manager = smonitor.get_manager()
    assert manager.config.level == "WARNING"
    smonitor.configure(level="CRITICAL", capture_warnings=False)
    ensure_configured(root)
    assert manager.config.level == "CRITICAL"
    ensure_configured(root, use_provider_policy=True)
    assert manager.config.level == "WARNING"


def test_first_bootstrap_prefers_application_project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tmp_path.joinpath("_smonitor.py").write_text(
        'SMONITOR = {"level": "CRITICAL", "profile": "qa"}\n'
    )
    ensure_configured(package(tmp_path, "provider"))
    assert smonitor.get_manager().config.level == "CRITICAL"
    assert smonitor.get_manager().config.profile == "qa"
    assert "provider" in smonitor.get_manager().get_codes()


def test_parallel_registration_is_idempotent(tmp_path):
    roots = [package(tmp_path, str(i)) for i in range(12)]
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(register_provider, roots * 3))
    manager = smonitor.get_manager()
    assert len(manager.get_codes()) == len(roots)
    assert len(manager.get_signals()) == len(roots)
    assert len(manager.get_providers()) == len(roots)
    assert not manager._policy_configured


def test_collision_rejects_whole_registration(tmp_path):
    first = package(tmp_path, "first", codes={"SHARED": {"message": "same"}})
    register_provider(first, provider="first")
    equal = package(tmp_path, "equal", codes={"SHARED": {"message": "same"}})
    register_provider(equal)
    manager = smonitor.get_manager()
    before = manager.get_codes(), manager.get_signals(), manager.get_providers()
    conflict = package(
        tmp_path,
        "conflict",
        codes={
            "NEW": {"message": "new"},
            "SHARED": {"message": "conflict"},
        },
    )
    with pytest.raises(ProviderRegistrationError) as caught:
        register_provider(conflict)
    assert caught.value.code == "SMONITOR-PROVIDER-CONFLICT"
    assert (manager.get_codes(), manager.get_signals(), manager.get_providers()) == before
    with pytest.raises(ProviderRegistrationError) as caught:
        register_provider(equal, provider="first")
    assert caught.value.code == "SMONITOR-PROVIDER-IDENTITY"
    assert (manager.get_codes(), manager.get_signals(), manager.get_providers()) == before


@pytest.mark.parametrize(
    "declaration", ['CODES = {"INVALID": "bad"}', 'raise RuntimeError("loader")']
)
def test_failed_registration_has_no_partial_state(tmp_path, declaration):
    root = tmp_path / "invalid"
    root.mkdir()
    root.joinpath("_smonitor.py").write_text(declaration)
    manager = smonitor.get_manager()
    with pytest.raises((ProviderRegistrationError, RuntimeError)):
        register_provider(root)
    assert manager.get_codes() == {}
    assert manager.get_signals() == {}
    assert manager.get_providers() == {}
    assert not manager._policy_configured
