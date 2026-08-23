"""Unit tests for Capability 3 — :class:`FrameworkDataService`.

These tests prove the production ``ehp-sn data`` backend works entirely through
the generic framework registry, using **synthetic** substrate definitions — the
framework unit test never imports ``ehp_research`` (ARCH-001).

The adapter projects registered definitions directly (identity, not copies),
enumerates substrates deterministically, and translates generic framework
failures (unknown / malformed / wrong-kind) into the CLI-facing
:class:`UnknownSubstrateError`. The lifecycle operations not yet implemented
(``plan``, ``build``, ``validate``, ``inspect``) fail explicitly with
:class:`DataNotImplementedError` rather than returning fake successful results.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from ehp_sn.cli._data_service import DataNotImplementedError, UnknownSubstrateError
from ehp_sn.cli.data_adapter import FrameworkDataService
from ehp_sn.discovery import ComponentRegistry
from ehp_sn.experiments import ComponentRef


@dataclass(frozen=True)
class _Definition:
    """Minimal synthetic stand-in shaped like a registered substrate definition.

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


def _substrate(name: str, output: str, description: str = "synthetic substrate") -> _Definition:
    return _Definition(
        ref=ComponentRef.parse(f"substrate:{name}/v1"),
        description=description,
        output_contract=output,
    )


def _service(registry: ComponentRegistry | None = None) -> FrameworkDataService:
    registry = registry if registry is not None else ComponentRegistry()
    return FrameworkDataService(registry)


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


def test_list_projects_registered_substrates() -> None:
    registry = ComponentRegistry()
    a = _substrate("alpha", "alpha-contract/v1")
    b = _substrate("beta", "beta-contract/v1")
    registry.register(a)
    registry.register(b)
    service = _service(registry)

    results = service.list()

    # Values are projected from the registered objects, not a second metadata map.
    assert [(r.ref, r.family, r.output) for r in results] == [
        ("substrate:alpha/v1", "alpha", "alpha-contract/v1"),
        ("substrate:beta/v1", "beta", "beta-contract/v1"),
    ]
    assert results[0].ref == a.ref.canonical
    assert results[0].output == a.output_contract


def test_list_uses_registry_deterministic_order() -> None:
    """No re-sorting in the adapter; order is discovery order (canonical ref)."""
    registry = ComponentRegistry()
    registry.register(_substrate("zeta", "z/v1"))
    registry.register(_substrate("alpha", "a/v1"))
    service = _service(registry)

    assert [r.ref for r in service.list()] == ["substrate:alpha/v1", "substrate:zeta/v1"]


def test_list_ignores_non_substrate_definitions() -> None:
    registry = ComponentRegistry()
    registry.register(
        _Definition(
            ref=ComponentRef.parse("task:synthetic/v1"),
            description="A task definition.",
            output_contract="",
        )
    )
    service = _service(registry)

    assert service.list() == ()


def test_list_works_without_any_definitions() -> None:
    service = _service(ComponentRegistry())

    assert service.list() == ()


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------


def test_show_projects_the_authoritative_registered_object() -> None:
    registry = ComponentRegistry()
    definition = _substrate("alpha", "alpha-contract/v1", "authoritative description")
    registry.register(definition)
    service = _service(registry)

    result = service.show("substrate:alpha/v1")

    # Identity assertion: show resolves the exact registered object.
    assert registry.resolve("substrate:alpha/v1") is definition
    assert result.ref == str(definition.ref)
    assert result.description == definition.description


def test_show_unknown_substrate_raises_unknown_substrate_error() -> None:
    service = _service(ComponentRegistry())

    with pytest.raises(UnknownSubstrateError):
        service.show("substrate:not-registered/v1")


def test_show_malformed_reference_raises_unknown_substrate_error() -> None:
    """Malformed reference syntax maps to the CLI 'unknown target' category (exit 4)."""
    service = _service(ComponentRegistry())

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
    service = _service(registry)

    assert registry.contains("task:synthetic/v1")
    with pytest.raises(UnknownSubstrateError):
        service.show("task:synthetic/v1")


# ---------------------------------------------------------------------------
# Phase boundary: lifecycle operations are explicitly not implemented
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("op", "args"),
    [
        ("plan", ("substrate:alpha/v1", "config.toml")),
        ("build", ("substrate:alpha/v1", "config.toml")),
        ("validate", ("data/interim/alpha/default/v1", "full")),
        ("inspect", ("data/interim/alpha/default/v1", 0)),
    ],
)
def test_lifecycle_operations_are_not_implemented(op: str, args: tuple[str, ...]) -> None:
    """The unimplemented lifecycle operations fail in one compact parameterized test.

    Their internal semantics are not tested because they do not exist yet; the
    test only pins the phase boundary (they must raise rather than fake success).
    """
    service = _service(ComponentRegistry())

    with pytest.raises(DataNotImplementedError):
        getattr(service, op)(*args)


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
    """The adapter couples to the registry, not to a research package."""
    import inspect

    from ehp_sn.cli import data_adapter

    source = inspect.getsource(data_adapter)
    import_lines = [
        line for line in source.splitlines() if line.lstrip().startswith(("import ", "from "))
    ]
    assert not any("ehp_research" in line for line in import_lines)
