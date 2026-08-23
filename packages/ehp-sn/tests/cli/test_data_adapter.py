"""Vertical tests for Capability 3 — :class:`FrameworkDataService`.

These tests prove the production ``ehp-sn data`` backend is backed by the real
generic registry populated through the Capability-2 provider registration:
``data list`` enumerates registered substrate definitions and ``data show``
resolves and projects the exact same authoritative definitions. The lifecycle
operations not yet implemented (``plan``, ``build``, ``validate``, ``inspect``)
fail explicitly with :class:`DataNotImplementedError` rather than returning fake
successful results.

The reader may freely import ``ehp_research`` here — these are tests, not
framework production code. The production adapter never imports it.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from ehp_research.registration import register_components
from ehp_research.substrates.dagflow import DAGFLOW_DEFINITION
from ehp_research.substrates.maze_nd import MAZE_ND_DEFINITION
from ehp_sn.cli._data_service import DataNotImplementedError, UnknownSubstrateError
from ehp_sn.cli.data_adapter import FrameworkDataService
from ehp_sn.discovery import ComponentRegistry
from ehp_sn.experiments import ComponentRef


@dataclass(frozen=True)
class _Definition:
    """Minimal structural stand-in shaped like a registered substrate definition.

    Carries the fields the adapter projects structurally (``ref``, ``kind``,
    ``description``, ``output_contract``). ``kind`` is derived from ``ref.kind``
    so tests can exercise both substrates and other component kinds.
    """

    ref: ComponentRef
    description: str
    output_contract: str

    @property
    def kind(self) -> str:
        return self.ref.kind


def _research_registry() -> ComponentRegistry:
    """A registry populated exactly like the installed provider does."""
    registry = ComponentRegistry()
    register_components(registry)
    return registry


def _service(registry: ComponentRegistry | None = None) -> FrameworkDataService:
    return FrameworkDataService(registry if registry is not None else _research_registry())


# ---------------------------------------------------------------------------
# Real list
# ---------------------------------------------------------------------------


def test_list_projects_exactly_the_registered_substrates() -> None:
    service = _service()

    results = service.list()

    refs = [(r.ref, r.family, r.output) for r in results]
    assert refs == [
        ("substrate:dagflow/v1", "dagflow", "simple-digraph/v1"),
        ("substrate:maze-nd/v1", "maze-nd", "raster-topology/v1"),
    ]


def test_list_ordering_follows_registry_deterministic_order() -> None:
    """No re-sorting in the adapter; order is the discovery order (by canonical ref)."""
    service = _service()

    results = service.list()
    assert [r.ref for r in results] == sorted(r.ref for r in results)


# ---------------------------------------------------------------------------
# Real show
# ---------------------------------------------------------------------------


def test_show_uses_the_authoritative_registered_object() -> None:
    registry = _research_registry()
    service = _service(registry)

    # The registry resolves to the exact authoritative object (identity).
    definition = registry.resolve("substrate:dagflow/v1")
    assert definition is DAGFLOW_DEFINITION

    result = service.show("substrate:dagflow/v1")

    assert result.ref == str(definition.ref)
    assert result.description == DAGFLOW_DEFINITION.description


def test_show_maze_nd_reflects_the_authoritative_definition() -> None:
    registry = _research_registry()
    service = _service(registry)

    assert service.show("substrate:maze-nd/v1").description == MAZE_ND_DEFINITION.description


# ---------------------------------------------------------------------------
# Same authority for list and show
# ---------------------------------------------------------------------------


def test_list_and_show_reflect_the_same_definition_authority() -> None:
    """A substituted definition X must drive both list and show — no second source."""
    registry = ComponentRegistry()
    custom = _Definition(
        ref=ComponentRef.parse("substrate:custom/v1"),
        description="An authoritative custom substrate description.",
        output_contract="my-contract/v1",
    )
    registry.register(custom)
    service = FrameworkDataService(registry)

    (listed,) = service.list()
    assert listed.ref == "substrate:custom/v1"
    assert listed.family == "custom"
    assert listed.output == "my-contract/v1"

    shown = service.show("substrate:custom/v1")
    assert shown.ref == "substrate:custom/v1"
    assert shown.description == custom.description


# ---------------------------------------------------------------------------
# Unknown / malformed / wrong kind
# ---------------------------------------------------------------------------


def test_show_unknown_substrate_raises_unknown_substrate_error() -> None:
    service = _service()

    with pytest.raises(UnknownSubstrateError):
        service.show("substrate:not-registered/v1")


def test_show_malformed_reference_raises_unknown_substrate_error() -> None:
    """Malformed reference syntax maps to the CLI 'unknown target' category (exit 4)."""
    service = _service()

    with pytest.raises(UnknownSubstrateError):
        service.show("not-a-reference")


def test_show_wrong_component_kind_is_rejected() -> None:
    """A reference that exists but is not a substrate is not acceptable to ``show``."""
    registry = ComponentRegistry()
    registry.register(
        _Definition(
            ref=ComponentRef.parse("task:synthetic/v1"),
            description="A task definition.",
            output_contract="",
        )
    )
    service = FrameworkDataService(registry)

    assert registry.contains("task:synthetic/v1")
    with pytest.raises(UnknownSubstrateError):
        service.show("task:synthetic/v1")


def test_list_with_non_substrate_definitions_ignores_them() -> None:
    """``data list`` enumerates substrates only; other component kinds are excluded."""
    registry = ComponentRegistry()
    registry.register(
        _Definition(
            ref=ComponentRef.parse("task:synthetic/v1"),
            description="A task definition.",
            output_contract="",
        )
    )
    service = FrameworkDataService(registry)

    assert service.list() == ()


# ---------------------------------------------------------------------------
# Future operations are explicitly not implemented
# ---------------------------------------------------------------------------


def test_plan_is_not_implemented() -> None:
    service = _service()

    with pytest.raises(DataNotImplementedError):
        service.plan("substrate:dagflow/v1", "config.toml")


def test_build_is_not_implemented() -> None:
    service = _service()

    with pytest.raises(DataNotImplementedError):
        service.build("substrate:dagflow/v1", "config.toml")


def test_validate_is_not_implemented() -> None:
    service = _service()

    with pytest.raises(DataNotImplementedError):
        service.validate("data/interim/dagflow/default/v1", "full")


def test_inspect_is_not_implemented() -> None:
    service = _service()

    with pytest.raises(DataNotImplementedError):
        service.inspect("data/interim/dagflow/default/v1", 0)


# ---------------------------------------------------------------------------
# Adapter is generic: no producer branches, no research import
# ---------------------------------------------------------------------------


def test_adapter_source_has_no_producer_conditionals() -> None:
    """The production adapter must name no substrate family and no research package."""
    import inspect

    from ehp_sn.cli import data_adapter

    source = inspect.getsource(data_adapter)
    for token in ("dagflow", "maze-nd", "ehp_research"):
        assert token not in source


def test_adapter_never_imports_ehp_research() -> None:
    """Structural guard: the adapter couples to the registry, not to research."""
    import inspect

    from ehp_sn.cli import data_adapter

    source = inspect.getsource(data_adapter)
    import_lines = [
        line for line in source.splitlines() if line.lstrip().startswith(("import ", "from "))
    ]
    assert not any("ehp_research" in line for line in import_lines)
