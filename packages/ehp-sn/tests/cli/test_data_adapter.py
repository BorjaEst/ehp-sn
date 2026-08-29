"""Unit tests for the CLI data adapter — :class:`FrameworkDataAdapter`.

These tests prove the production ``ehp-sn data`` adapter works entirely through
the generic framework registry, using **synthetic** substrate definitions — the
framework unit test never imports ``ehp_research`` (ARCH-001).

The adapter projects registered definitions directly (identity, not copies),
enumerates substrates deterministically, and translates generic framework
failures (unknown / malformed / wrong-kind) into the CLI-facing
:class:`UnknownSubstrateError`. The ``plan`` projection returns explicit CLI
presentation DTOs and never leaks framework value objects, and ``build`` and
``inspect`` delegate to the generic framework lifecycles and project their
outcomes.

``data inspect ARTIFACT --record RECORD_ID`` (Phase 0R) is the deterministic
generic exact-record inspection path: committed substrate artifacts built over
synthetic producers resolve the exact record through the existing record-identity
mechanism with no producer-specific or contract-specific branch. The adapter
tests here prove this is producer-neutral by inspecting records originating from
two differently-shaped synthetic producers.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest
from ehp_sn.artifacts import publish_artifact
from ehp_sn.cli.data_adapter import (
    ConfigurationInvalidError,
    ConfigurationUnreadableError,
    FrameworkDataAdapter,
    IdentityInputView,
    InspectResult,
    RecordNotFoundError,
    ResolvedResourceView,
    UnknownArtifactError,
    UnknownSubstrateError,
)
from ehp_sn.configuration import LoadedConfiguration
from ehp_sn.discovery import ComponentRegistry
from ehp_sn.execution import (
    GeneratedRecordBody,
    MaterializationSession,
    RealizationKey,
    SubstrateExecutionComposition,
    SubstrateExecutionRegistration,
    execute_substrate,
)
from ehp_sn.experiments import ComponentRef
from ehp_sn.planning import (
    IdentityInput,
    PlanningDeclaration,
    PlanningResolver,
    ReleaseCoordinate,
    ResourceRequirement,
    SubstratePlanningComposition,
    SubstratePlanningRegistration,
    plan_substrate,
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
        execution_composition=SubstrateExecutionComposition(()),
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

    service = FrameworkDataAdapter(
        registry,
        planning_composition=composition,
        execution_composition=SubstrateExecutionComposition(()),
    )
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
    service = FrameworkDataAdapter(
        registry,
        planning_composition=composition,
        execution_composition=SubstrateExecutionComposition(()),
    )

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
        execution_composition=SubstrateExecutionComposition(()),
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
    service = FrameworkDataAdapter(
        registry,
        planning_composition=composition,
        execution_composition=SubstrateExecutionComposition(()),
    )

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


def test_adapter_source_has_no_figure_branches_or_imports() -> None:
    """Generic inspection must be free of figure-specific branches and imports.

    ``data inspect`` (P0R-3) must not require any figure framework import and
    must not branch on a figure concept; figure semantics belong downstream in
    the figure phases, not in the generic inspection path.
    """
    import inspect

    from ehp_sn.cli import data_adapter

    source = inspect.getsource(data_adapter)
    import_lines = [
        line for line in source.splitlines() if line.lstrip().startswith(("import ", "from "))
    ]
    assert not any(
        line.lstrip().startswith(("from ehp_sn.figures", "from matplotlib", "import matplotlib"))
        for line in import_lines
    )
    for token in ("FigureSpec", "FigureProjection", "matplotlib", "renderer"):
        assert token.lower() not in source.lower()


def test_adapter_never_imports_ehp_research() -> None:
    """The adapter couples to the registry, not to a research package."""
    import inspect

    from ehp_sn.cli import data_adapter

    source = inspect.getsource(data_adapter)
    import_lines = [
        line for line in source.splitlines() if line.lstrip().startswith(("import ", "from "))
    ]
    assert not any("ehp_research" in line for line in import_lines)


# ---------------------------------------------------------------------------
# inspect: deterministic generic exact-record path (Phase 0R P0R-3)
# ---------------------------------------------------------------------------


class _Resolver:
    """Minimal generic resource resolver (definitions with no resource deps)."""

    def resolve(self, requirement: ResourceRequirement):
        from ehp_sn.planning import ResolvedResource, ResourceResolutionError

        if requirement.definition_resource_ref is None:
            raise ResourceResolutionError(f"no declared reference for {requirement.ref!r}")
        return ResolvedResource(
            requirement_ref=requirement.ref,
            resource_ref=requirement.definition_resource_ref,
            resolution_source="definition",
        )


def _producer_family(interim_root: Path, family: str, *, records_by_index, output_contract: str):
    """Build and commit a synthetic substrate artifact under ``interim_root``.

    The producer carries no resource requirements and derives a deterministic
    ``record_id`` for each record through the existing framework record-identity
    mechanism, so the committed artifact's records are addressable by
    ``record_id``. Returns ``(release_dir, adapter)`` where ``release_dir`` is
    the physical committed release directory under ``interim_root`` and
    ``adapter`` is a :class:`FrameworkDataAdapter` rooted at ``interim_root``.
    """
    from ehp_sn.artifacts import assemble_artifact

    registry = ComponentRegistry()
    ref = ComponentRef.parse(f"substrate:{family}/v1")
    definition = _Definition(
        ref=ref,
        description=f"{family} substrate",
        output_contract=output_contract,
    )
    registry.register(definition)
    variant = family

    def _plan(document: LoadedConfiguration) -> PlanningDeclaration:
        return PlanningDeclaration(
            configuration={"value": 1},
            resources=(),
            identity_inputs=(IdentityInput("variant", variant),),
        )

    def _execute(session: MaterializationSession) -> None:
        for index, content in records_by_index.items():
            session.add_record(
                GeneratedRecordBody(
                    content=content,
                    realization_key=RealizationKey(inputs=(IdentityInput("realization_index", index),)),
                )
            )

    planning = SubstratePlanningComposition(
        (SubstratePlanningRegistration(definition=definition, plan=_plan),)
    )
    execution = SubstrateExecutionComposition(
        (SubstrateExecutionRegistration(definition=definition, execute=_execute),)
    )
    document = LoadedConfiguration(
        source=Path("x.toml"),
        values={"substrate": {"variant": variant}, "release": 1},
    )
    plan = plan_substrate(registry, planning, ref, document, resource_resolver=_Resolver())
    result = execute_substrate(registry, execution, plan)
    assembled = assemble_artifact(plan, result)
    coordinate = ReleaseCoordinate(family=family, variant=variant, release=1)
    publish_artifact(assembled, root=interim_root, coordinate=coordinate)
    adapter = FrameworkDataAdapter(
        ComponentRegistry(),
        planning_composition=SubstratePlanningComposition(()),
        execution_composition=SubstrateExecutionComposition(()),
        root=interim_root,
    )
    return interim_root / family / variant / "v1", adapter


def _adapter(interim_root: Path) -> FrameworkDataAdapter:
    return FrameworkDataAdapter(
        ComponentRegistry(),
        planning_composition=SubstratePlanningComposition(()),
        execution_composition=SubstrateExecutionComposition(()),
        root=interim_root,
    )


def _record_ids(release_dir: Path) -> list[str]:
    from ehp_sn.artifacts import load_release

    return [r.record_id for r in load_release(release_dir).records]


def test_inspect_resolves_exact_record(tmp_path: Path) -> None:
    """Given a committed artifact and an exact record_id, inspect returns exactly it."""
    release_dir, adapter = _producer_family(
        tmp_path / "interim",
        "alpha",
        records_by_index={1: {"kind": "graph", "nodes": 4}, 2: {"kind": "graph", "nodes": 8}},
        output_contract="graph-v1",
    )
    first_id = _record_ids(release_dir)[0]

    result = adapter.inspect(str(release_dir), first_id)

    assert isinstance(result, InspectResult)
    assert result.record_id == first_id
    assert result.schema_ref == "graph-v1"
    # The content is the exact record for the first realization_index.
    assert result.content in ({"kind": "graph", "nodes": 4}, {"kind": "graph", "nodes": 8})


def test_inspect_by_artifact_reference_matches_path_lookup(tmp_path: Path) -> None:
    """Inspecting by ``artifact:`` reference resolves the same record as the path."""
    release_dir, adapter = _producer_family(
        tmp_path / "interim",
        "beta",
        records_by_index={7: {"value": "beta-7"}},
        output_contract="beta-v1",
    )
    only_id = _record_ids(release_dir)[0]

    by_path = adapter.inspect(str(release_dir), only_id)
    by_ref = adapter.inspect("artifact:beta/beta/v1", only_id)

    assert by_ref.artifact_ref == "artifact:beta/beta/v1"
    assert by_ref.record_id == by_path.record_id
    assert by_ref.content == by_path.content


def test_inspect_unknown_record_raises_record_not_found(tmp_path: Path) -> None:
    release_dir, adapter = _producer_family(
        tmp_path / "interim",
        "gamma",
        records_by_index={1: {"value": 1}},
        output_contract="gamma-v1",
    )

    with pytest.raises(RecordNotFoundError):
        adapter.inspect(str(release_dir), "sha256:no-such-record")


def test_inspect_unknown_artifact_raises_unknown_artifact(tmp_path: Path) -> None:
    adapter = _adapter(tmp_path / "interim")
    with pytest.raises(UnknownArtifactError):
        adapter.inspect(str(tmp_path / "interim" / "missing"), "any")
    with pytest.raises(UnknownArtifactError):
        adapter.inspect("artifact:missing/missing/v1", "any")
    # A malformed artifact reference is also a controlled unknown-artifact error.
    with pytest.raises(UnknownArtifactError):
        adapter.inspect("artifact:missing/v1", "any")


def test_inspect_is_producer_neutral(tmp_path: Path) -> None:
    """Records from two differently-shaped producers inspect through one generic path."""
    release_a, _ = _producer_family(
        tmp_path / "interim",
        "producer-a",
        records_by_index={1: {"edges": [[0, 1]]}},
        output_contract="graph-v1",
    )
    release_b, adapter = _producer_family(
        tmp_path / "interim",
        "producer-b",
        records_by_index={3: {"field": {"r": 1, "c": 2}, "class": 4}},
        output_contract="field-v1",
    )

    a = adapter.inspect(str(release_a), _record_ids(release_a)[0])
    b = adapter.inspect(str(release_b), _record_ids(release_b)[0])

    # No branch changed the generic shape: artifact+record+schema+content only.
    assert a.schema_ref == "graph-v1" and b.schema_ref == "field-v1"
    assert a.content == {"edges": [[0, 1]]}
    assert b.content == {"field": {"r": 1, "c": 2}, "class": 4}


def test_inspect_deterministic_lookup(tmp_path: Path) -> None:
    """Repeated inspection of the same artifact+record resolves the same record."""
    release_dir, adapter = _producer_family(
        tmp_path / "interim",
        "delta",
        records_by_index={1: {"a": 1}, 2: {"a": 2}},
        output_contract="delta-v1",
    )
    first_id = _record_ids(release_dir)[0]

    first = adapter.inspect(str(release_dir), first_id)
    second = adapter.inspect(str(release_dir), first_id)

    assert first == second
    assert first.record_id == first_id
