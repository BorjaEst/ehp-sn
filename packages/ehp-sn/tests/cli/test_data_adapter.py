"""Unit tests for the CLI data adapter — :class:`FrameworkDataAdapter`.

These tests prove the production ``ehp-sn data`` adapter works entirely through
the generic framework registry, using **synthetic** substrate definitions — the
framework unit test never imports ``ehp_research`` (ARCH-001).

The adapter projects registered definitions directly (identity, not copies),
enumerates substrates deterministically, and translates generic framework
failures (unknown / malformed / wrong-kind) into the CLI-facing
:class:`UnknownSubstrateError`. The ``plan`` projection returns explicit CLI
presentation DTOs and never leaks framework value objects. ``build``,
``validate`` and ``inspect`` are not part of the adapter surface (they are
reported unsupported by the CLI itself); no fake lifecycle method pretends they
exist.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from ehp_sn.cli.data_adapter import (
    ConfigurationInvalidError,
    ConfigurationUnreadableError,
    FrameworkDataAdapter,
    IdentityInputView,
    ResolvedResourceView,
    UnknownSubstrateError,
)
from ehp_sn.configuration import LoadedConfiguration
from ehp_sn.discovery import ComponentRegistry
from ehp_sn.experiments import ComponentRef
from ehp_sn.planning import (
    IdentityInput,
    PlanningDeclaration,
    PlanningResolver,
    ResourceRequirement,
    SubstratePlanningComposition,
    SubstratePlanningRegistration,
)


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


def _service(
    registry: ComponentRegistry | None = None,
    planning_composition: SubstratePlanningComposition | None = None,
) -> FrameworkDataAdapter:
    registry = registry if registry is not None else ComponentRegistry()
    planning_composition = planning_composition or SubstratePlanningComposition(())
    return FrameworkDataAdapter(
        registry,
        planning_composition=planning_composition,
    )


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
# plan: delegates to the generic planning orchestration, then projects
# ---------------------------------------------------------------------------


def _declaring_plan(
    resources: tuple[ResourceRequirement, ...] = (),
    identity: tuple[IdentityInput, ...] = (),
) -> PlanningResolver:
    """A synthetic planning resolver producing a fixed declaration."""

    def plan(document: LoadedConfiguration) -> PlanningDeclaration:
        return PlanningDeclaration(
            configuration={"synthetic": True},
            resources=resources,
            identity_inputs=identity,
        )

    return plan


@pytest.fixture()
def plan_registry(tmp_path):
    """A registry with one synthetic substrate + planning composition, and a config path.

    Returns ``(service, config_path, definition)`` so tests can call
    ``service.plan`` through the real generic loading + planning path with
    synthetic (non-research) components.
    """
    registry = ComponentRegistry()
    definition = _substrate("alpha", "alpha-contract/v1", "synthetic substrate")
    registry.register(definition)

    composition = SubstratePlanningComposition(
        (SubstratePlanningRegistration(definition=definition, plan=_declaring_plan()),)
    )

    config_path = tmp_path / "config.toml"
    config_path.write_text('[substrate]\nvariant = "default"\n', encoding="utf-8")

    service = FrameworkDataAdapter(registry, planning_composition=composition)
    return service, config_path, definition


def test_plan_requires_config(plan_registry) -> None:
    service, _, _ = plan_registry

    with pytest.raises(ConfigurationInvalidError):
        service.plan("substrate:alpha/v1", None)


def test_plan_projects_authoritative_plan(plan_registry) -> None:
    service, config_path, definition = plan_registry

    # Re-compose with a source requirement + identity to check projection width.
    registry = ComponentRegistry()
    registry.register(definition)
    from ehp_sn.planning import CARDINALITY_ONE

    composition = SubstratePlanningComposition(
        (
            SubstratePlanningRegistration(
                definition=definition,
                plan=_declaring_plan(
                    resources=(
                        ResourceRequirement(
                            ref="requirement:substrate/alpha-source/v1",
                            resource_kind="raw-source",
                            accepted_schema_ids=("raw/v1",),
                            cardinality=CARDINALITY_ONE,
                            definition_resource_ref="UNRESOLVED-SYNTHETIC",
                            description="synthetic source",
                        ),
                    ),
                    identity=(
                        IdentityInput(name="variant", value="default"),
                        IdentityInput(name="seed", value=42),
                    ),
                ),
            ),
        )
    )
    service = FrameworkDataAdapter(registry, planning_composition=composition)

    result = service.plan("substrate:alpha/v1", str(config_path))

    # Projection comes from the authoritative plan: target + output contract
    # derived from the registered definition; bound resource + identity exactly
    # as planned, projected into CLI presentation values (never the framework
    # value objects).
    assert result.target == "substrate:alpha/v1"
    assert result.output_contract == "alpha-contract/v1"
    assert len(result.resources) == 1
    assert isinstance(result.resources[0], ResolvedResourceView)
    assert result.resources[0].resource_ref == "UNRESOLVED-SYNTHETIC"
    assert result.resources[0].resolution_source == "definition"
    assert all(isinstance(item, IdentityInputView) for item in result.identity)
    assert [(i.name, i.value) for i in result.identity] == [
        ("variant", "default"),
        ("seed", 42),
    ]


def test_plan_does_not_serialize_producer_configuration(plan_registry) -> None:
    """The projection never exposes the opaque producer configuration object."""
    service, config_path, _ = plan_registry

    result = service.plan("substrate:alpha/v1", str(config_path))

    # The opaque configuration is deliberately not part of the CLI projection.
    assert not hasattr(result, "configuration")


def test_plan_unknown_substrate_is_translated(plan_registry) -> None:
    service, config_path, _ = plan_registry

    with pytest.raises(UnknownSubstrateError):
        service.plan("substrate:not-registered/v1", str(config_path))


def test_plan_missing_resolver_is_unknown_substrate(plan_registry) -> None:
    service, config_path, definition = plan_registry
    # A target registered in discovery but absent from the planning composition
    # cannot be planned; it surfaces as an unknown-substrate CLI category.
    registry = ComponentRegistry()
    registry.register(definition)
    service = FrameworkDataAdapter(
        registry,
        planning_composition=SubstratePlanningComposition(()),
    )
    with pytest.raises(UnknownSubstrateError):
        service.plan("substrate:alpha/v1", str(config_path))


def test_plan_unreadable_config_is_configuration_unreadable(plan_registry, tmp_path) -> None:
    service, _, _ = plan_registry
    missing = tmp_path / "missing.toml"

    with pytest.raises(ConfigurationUnreadableError):
        service.plan("substrate:alpha/v1", str(missing))


def test_plan_malformed_config_is_configuration_invalid(plan_registry) -> None:
    service, config_path, _ = plan_registry
    config_path.write_text("this is [ not valid toml", encoding="utf-8")

    with pytest.raises(ConfigurationInvalidError):
        service.plan("substrate:alpha/v1", str(config_path))


def test_plan_producer_failure_is_configuration_invalid(plan_registry) -> None:
    """A generic producer-resolution failure maps to the invalid-configuration category.

    The synthetic resolver raises a generic exception; the framework planning
    boundary normalizes it into :class:`ProducerResolutionError`, and the
    adapter maps that generic error — not any producer-specific class — to
    ``ConfigurationInvalidError``.
    """
    service, config_path, definition = plan_registry
    registry = ComponentRegistry()
    registry.register(definition)

    def exploding(document: LoadedConfiguration) -> PlanningDeclaration:
        raise ValueError("producer semantics rejected the configuration")

    composition = SubstratePlanningComposition(
        (SubstratePlanningRegistration(definition=definition, plan=exploding),)
    )
    service = FrameworkDataAdapter(registry, planning_composition=composition)

    with pytest.raises(ConfigurationInvalidError):
        service.plan("substrate:alpha/v1", str(config_path))


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
