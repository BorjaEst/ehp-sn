"""Tests for Capability 3 — the generic provider/composition bootstrap.

The framework must obtain the effective registry from installed downstream
providers without importing any research package by name and without a
``try/except ImportError`` fallback. These tests exercise
:func:`ehp_sn.discovery.register_installed_providers` and
:func:`ehp_sn.discovery.effective_registry`.

Most tests run against *fake* entry points (monkeypatched entry-point metadata)
so they are independent of whether ``ehp_research`` is installed. One
integration test confirms the real installed provider (``ehp_research``) is
picked up and populates the registry with Dagflow and Maze-ND.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from ehp_sn.discovery import (
    PROVIDER_ENTRY_POINT_GROUP,
    ComponentRegistry,
    effective_registry,
    register_installed_providers,
)
from ehp_sn.discovery import providers as providers_module
from ehp_sn.experiments import ComponentRef


@dataclass(frozen=True)
class _FakeEntryPoint:
    """Minimal stand-in for ``importlib.metadata.EntryPoint``."""

    name: str
    value: str
    group: str = PROVIDER_ENTRY_POINT_GROUP

    def load(self):
        # ``value`` names a module:attr; resolve here like entry_point.load() does.
        module_name, _, attr = self.value.partition(":")
        import importlib

        module = importlib.import_module(module_name)
        return getattr(module, attr)


@dataclass(frozen=True)
class _Definition:
    ref: ComponentRef
    description: str
    output_contract: str

    @property
    def kind(self) -> str:
        return self.ref.kind


# A provider function living in this test module, referenced by dotted path.
def _register_test_providers(registry: ComponentRegistry) -> None:
    registry.register(
        _Definition(
            ref=ComponentRef.parse("substrate:test/v1"),
            description="A test substrate.",
            output_contract="test-contract/v1",
        )
    )


def test_register_installed_providers_invokes_providers(monkeypatch: pytest.MonkeyPatch) -> None:
    entry_points = [
        _FakeEntryPoint(
            name="test",
            value=f"{__name__}:_register_test_providers",
        )
    ]

    def _fake_entry_points(*, group: str | None = None):
        return entry_points

    monkeypatch.setattr(providers_module.metadata, "entry_points", _fake_entry_points)

    registry = ComponentRegistry()
    returned = register_installed_providers(registry)

    assert returned is registry
    assert registry.contains("substrate:test/v1")


def test_effective_registry_populates_from_providers(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake_entry_points(*, group: str | None = None):
        return [_FakeEntryPoint(name="test", value=f"{__name__}:_register_test_providers")]

    monkeypatch.setattr(providers_module.metadata, "entry_points", _fake_entry_points)

    registry = effective_registry()

    assert registry.contains("substrate:test/v1")


def test_no_installed_providers_yields_empty_effective_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fake_entry_points(*, group: str | None = None):
        return []

    monkeypatch.setattr(providers_module.metadata, "entry_points", _fake_entry_points)

    assert list(effective_registry().iter()) == []


# ---------------------------------------------------------------------------
# Real installed provider (integration)
# ---------------------------------------------------------------------------


def test_effective_registry_picks_up_installed_research_provider() -> None:
    """When ``ehp_research`` is installed, the effective registry gets Dagflow + Maze-ND.

    This proves the production composition path: research definitions reach the
    registry through the generic entry-point provider mechanism, not through a
    framework import of ``ehp_research``.
    """
    try:
        import ehp_research  # noqa: F401
    except ImportError:  # pragma: no cover - skipping when not installed
        pytest.skip("ehp_research is not installed")

    registry = effective_registry()

    canonical_refs = sorted(d.ref.canonical for d in registry.iter(kind="substrate"))
    assert canonical_refs == ["substrate:dagflow/v1", "substrate:maze-nd/v1"]
