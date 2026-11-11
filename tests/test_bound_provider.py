"""Explicit root snapshots retain existing setup/reset and path semantics."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

import smonitor
from smonitor.integrations import (
    bind_provider,
    emit_from_catalog,
    ensure_configured,
    reset_configured_packages,
)

ENTRY = {"code": "BOUND-W001", "source": "bound.test", "level": "WARNING"}


def provider(root, name="bound"):
    root.mkdir(exist_ok=True)
    (root / "_smonitor.py").write_text(
        f'PROFILE = "dev"\nCODES = {{"BOUND-W001": {{"message": "{name}"}}}}\n',
        encoding="utf-8",
    )
    return root


@pytest.mark.parametrize("bootstrap", [True, False])
def test_bound_emission_has_no_warm_path_resolution(tmp_path, monkeypatch, bootstrap):
    root = bind_provider(provider(tmp_path / "provider"))
    smonitor.configure(profile="agent", level="WARNING", capture_logging=False)
    first = emit_from_catalog(ENTRY, package_root=root, bootstrap_policy=bootstrap)
    original = Path.resolve
    resolutions = []

    def counted(path, *args, **kwargs):
        resolutions.append(path)
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", counted)
    for _ in range(100):
        event = emit_from_catalog(ENTRY, package_root=root, bootstrap_policy=bootstrap)
        assert (event["code"], event["message"]) == (first["code"], first["message"])
    assert not resolutions
    assert smonitor.get_manager().config.profile == "agent"


def test_bound_configuration_respects_reset_and_force(tmp_path, monkeypatch):
    root = bind_provider(provider(tmp_path / "provider"))
    calls = []
    original = smonitor.configure

    def configure(**kwargs):
        calls.append(kwargs)
        return original(**kwargs)

    monkeypatch.setattr(smonitor, "configure", configure)
    ensure_configured(root)
    ensure_configured(root)
    assert len(calls) == 1
    reset_configured_packages()
    ensure_configured(root)
    # Existing application policy survives ordinary registration after reset.
    assert len(calls) == 1
    ensure_configured(root, use_provider_policy=True)
    assert len(calls) == 2


def test_bound_provider_survives_manager_replacement(tmp_path, monkeypatch):
    from smonitor.core import manager as module

    root = bind_provider(provider(tmp_path / "provider"))
    ensure_configured(root)
    replacement = module.Manager()
    monkeypatch.setattr(module, "_manager_singleton", replacement)
    assert emit_from_catalog(ENTRY, package_root=root)["message"] == "bound"
    assert str(root.package_root) in replacement._configured_packages


def test_binding_is_explicit_snapshot_of_relative_root(tmp_path, monkeypatch):
    first = provider(tmp_path / "first")
    second = provider(tmp_path / "second")
    monkeypatch.chdir(first)
    root = bind_provider(Path("."))
    monkeypatch.chdir(second)
    ensure_configured(root)
    ensure_configured(Path("."))
    assert smonitor.get_manager()._configured_packages == {str(first), str(second)}


def test_plain_symlink_inputs_follow_retargeting(tmp_path):
    first = provider(tmp_path / "first")
    second = provider(tmp_path / "second")
    link = tmp_path / "link"
    try:
        link.symlink_to(first, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlinks unavailable")
    root = bind_provider(link)
    ensure_configured(link)
    link.unlink()
    link.symlink_to(second, target_is_directory=True)
    ensure_configured(link)
    assert root.package_root == first
    assert smonitor.get_manager()._configured_packages == {str(first), str(second)}


def test_bound_concurrent_first_use_registers_once(tmp_path, monkeypatch):
    from smonitor.integrations import provider as module

    root = bind_provider(provider(tmp_path / "provider"))
    calls = []
    original = module.register_provider

    def register(path, **kwargs):
        calls.append(path)
        return original(path, **kwargs)

    monkeypatch.setattr(module, "register_provider", register)
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda _: ensure_configured(root), range(32)))
    assert calls == [root.package_root]
