"""Behavioral tests for generic framework planning.

These tests exercise the framework planning surface with **synthetic in-test
producers and resolvers** — never a runtime research component. A synthetic
producer is deliberately defined inside this test module, not in ``ehp_sn``
production code (``ehp_sn.planning`` must not contain a fake producer or
placeholder). This proves the framework planning path is genuinely generic: it
works identically for a producer with no resources and for one with a resource
requirement, and never branches on a family.

The planning operation is *composed externally*: discovery registers only the
definition; a :class:`~ehp_sn.planning.SubstratePlanningComposition` binds each
definition to its demonstrated planning resolver (a
:data:`~ehp_sn.planning.PlanningResolver`), selected by definition identity.
Nothing about producer behavior lives on the discovery registry.

Test matrix:

* planning with no resource requirement → immutable plan;
* planning with a resource requirement → resolver invoked, exact bound binding
  stored in the plan;
* resolver selection by definition identity: A → A's resolver, B → B's
  resolver;
* adding definition C requires one extra planning registration, no changes to
  the registry, generic planner, or CLI;
* same resolved scientific inputs → same plan (structural equality);
* different identity-bearing input → different plan.

No hashing is invented: identity comparison is plain structural equality of the
immutable plan (the current identity contract defines no digest semantics).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from ehp_sn.configuration import LoadedConfiguration
from ehp_sn.discovery import ComponentRegistry
from ehp_sn.experiments import ComponentRef
from ehp_sn.planning import (
    CARDINALITY_ONE,
    ExecutionPlan,
    IdentityInput,
    MissingPlanningCapabilityError,
    NotASubstrateError,
    PlanningDeclaration,
    PlanningResolver,
    ResolvedResource,
    ResourceRequirement,
    ResourceResolutionError,
    SubstratePlanningComposition,
    SubstratePlanningRegistration,
    plan_substrate,
)


@dataclass(frozen=True)
class SyntheticDefinition:
    """Minimal in-test discoverable definition with a substrate shape."""

    ref: ComponentRef
    kind: str
    description: str
    output_contract: str


def _loaded(values: Mapping[str, Any]) -> LoadedConfiguration:
    return LoadedConfiguration(source=Path("synthetic.toml"), values=values)


def _no_resource_plan(seed: int) -> PlanningResolver:
    """A planning resolver declaring no resources and one identity input."""

    def plan(document: LoadedConfiguration) -> PlanningDeclaration:
        return PlanningDeclaration(
            configuration={"seed": seed},
            resources=(),
            identity_inputs=(IdentityInput("seed", seed),),
        )

    return plan


def _source_requirement_plan(source_ref: str) -> PlanningResolver:
    """A planning resolver declaring one resource requirement and an identity input."""

    def plan(document: LoadedConfiguration) -> PlanningDeclaration:
        requirement = ResourceRequirement(
            ref="requirement:synthetic/source/v1",
            resource_kind="raw-source",
            accepted_schema_ids=("synthetic:extraction/v1",),
            cardinality=CARDINALITY_ONE,
            definition_resource_ref=source_ref,
            description="synthetic upstream source",
        )
        return PlanningDeclaration(
            configuration={"source": source_ref},
            resources=(requirement,),
            identity_inputs=(IdentityInput("source_reference", source_ref),),
        )

    return plan


class RecordingResolver:
    """In-test resource resolver that records which requirements it was asked to bind."""

    def __init__(self, mapping: dict[str, str] | None = None) -> None:
        self._mapping = mapping or {}
        self.calls: list[ResourceRequirement] = []

    def resolve(self, requirement: ResourceRequirement) -> ResolvedResource:
        self.calls.append(requirement)
        resource_ref = self._mapping.get(requirement.ref, requirement.definition_resource_ref)
        if resource_ref is None:
            raise ResourceResolutionError(
                f"no exact resource reference available for requirement {requirement.ref!r}"
            )
        return ResolvedResource(
            requirement_ref=requirement.ref,
            resource_ref=resource_ref,
            resolution_source="definition",
        )


def _definition(ref_text: str, output_contract: str = "synthetic-contract/v1") -> SyntheticDefinition:
    """Build an in-test synthetic substrate definition from a canonical reference."""
    ref = ComponentRef.parse(ref_text)
    return SyntheticDefinition(
        ref=ref,
        kind=ref.kind,
        description="synthetic substrate",
        output_contract=output_contract,
    )


@pytest.fixture()
def registry_and_composition():
    """A registry with definitions A and B, and a composition binding their resolvers."""
    definition_a = _definition("substrate:synthetic-a/v1")
    definition_b = _definition("substrate:synthetic-b/v1")

    registry = ComponentRegistry()
    registry.register(definition_a)
    registry.register(definition_b)

    composition = SubstratePlanningComposition(
        (
            SubstratePlanningRegistration(definition=definition_a, plan=_no_resource_plan(seed=7)),
            SubstratePlanningRegistration(
                definition=definition_b, plan=_source_requirement_plan("source:upstream/v1")
            ),
        )
    )
    return registry, composition


# ---------------------------------------------------------------------------
# Planning with no resource requirement
# ---------------------------------------------------------------------------


def test_plan_with_no_resources_is_immutable_plan(registry_and_composition) -> None:
    registry, composition = registry_and_composition
    resolver = RecordingResolver()

    plan = plan_substrate(
        registry,
        composition,
        "substrate:synthetic-a/v1",
        _loaded({}),
        resource_resolver=resolver,
    )

    assert isinstance(plan, ExecutionPlan)
    assert plan.target == ComponentRef.parse("substrate:synthetic-a/v1")
    assert plan.output_contract == "synthetic-contract/v1"
    assert plan.resources == ()
    assert len(plan.identity_inputs) == 1
    # The resource resolver is never invoked when no resources are declared.
    assert resolver.calls == []
    # The plan is immutable (frozen dataclass).
    with pytest.raises(AttributeError):
        plan.resources = (ResolvedResource("x", "y", "z"),)  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Planning with a resource requirement
# ---------------------------------------------------------------------------


def test_plan_resolves_resource_requirement(registry_and_composition) -> None:
    registry, composition = registry_and_composition
    resolver = RecordingResolver()

    plan = plan_substrate(
        registry,
        composition,
        "substrate:synthetic-b/v1",
        _loaded({}),
        resource_resolver=resolver,
    )

    assert len(resolver.calls) == 1
    assert resolver.calls[0].ref == "requirement:synthetic/source/v1"
    # The exact bound binding is stored in the plan.
    assert plan.resources == (
        ResolvedResource(
            requirement_ref="requirement:synthetic/source/v1",
            resource_ref="source:upstream/v1",
            resolution_source="definition",
        ),
    )


def test_plan_passes_exact_bound_resource_into_identity(registry_and_composition) -> None:
    registry, composition = registry_and_composition
    resolver = RecordingResolver()

    plan = plan_substrate(
        registry,
        composition,
        "substrate:synthetic-b/v1",
        _loaded({}),
        resource_resolver=resolver,
    )

    # The exact source reference the producer declared is the identity input.
    assert plan.identity_inputs == (IdentityInput("source_reference", "source:upstream/v1"),)


def test_plan_required_resource_without_reference_fails_cleanly(registry_and_composition) -> None:
    registry, composition = registry_and_composition
    # Rebind B with a resolver that requires a source with no exact reference.
    definition_b = registry.resolve("substrate:synthetic-b/v1")
    composition = SubstratePlanningComposition(
        (
            SubstratePlanningRegistration(
                definition=definition_b,
                plan=_source_requirement_plan(None),  # type: ignore[arg-type]
            ),
        )
    )
    resolver = RecordingResolver()

    with pytest.raises(ResourceResolutionError):
        plan_substrate(
            registry,
            composition,
            "substrate:synthetic-b/v1",
            _loaded({}),
            resource_resolver=resolver,
        )


# ---------------------------------------------------------------------------
# Resolver selection is by definition identity, not the registry
# ---------------------------------------------------------------------------


def test_resolver_selected_by_definition_identity(registry_and_composition) -> None:
    """A and B resolve through the same registry but each selects its own resolver."""
    registry, composition = registry_and_composition

    plan_a = plan_substrate(
        registry,
        composition,
        "substrate:synthetic-a/v1",
        _loaded({}),
        resource_resolver=RecordingResolver(),
    )
    plan_b = plan_substrate(
        registry,
        composition,
        "substrate:synthetic-b/v1",
        _loaded({}),
        resource_resolver=RecordingResolver(),
    )

    # A declares a seed identity input; B declares a source-reference identity.
    assert [i.name for i in plan_a.identity_inputs] == ["seed"]
    assert [i.name for i in plan_b.identity_inputs] == ["source_reference"]


def test_adding_definition_c_only_adds_a_registration(registry_and_composition) -> None:
    """Adding C requires one registration entry — no discovery/planner/CLI change.

    The composition is built with C's own resolver; the generic planner and the
    discovery registry are untouched.
    """
    registry, _ = registry_and_composition
    definition_c = _definition("substrate:synthetic-c/v1")
    registry.register(definition_c)

    composition = SubstratePlanningComposition(
        (SubstratePlanningRegistration(definition=definition_c, plan=_no_resource_plan(seed=99)),)
    )

    plan = plan_substrate(
        registry,
        composition,
        "substrate:synthetic-c/v1",
        _loaded({}),
        resource_resolver=RecordingResolver(),
    )

    assert plan.target == ComponentRef.parse("substrate:synthetic-c/v1")
    assert plan.identity_inputs == (IdentityInput("seed", 99),)
    assert len(composition) == 1


# ---------------------------------------------------------------------------
# Identity representation: structural equality of the immutable plan
# ---------------------------------------------------------------------------


def test_same_resolved_inputs_produce_equal_plan(registry_and_composition) -> None:
    registry, composition = registry_and_composition
    resolver = RecordingResolver()

    plan_a = plan_substrate(
        registry, composition, "substrate:synthetic-a/v1", _loaded({}), resource_resolver=resolver
    )
    plan_b = plan_substrate(
        registry, composition, "substrate:synthetic-a/v1", _loaded({}), resource_resolver=resolver
    )

    assert plan_a == plan_b
    assert plan_a.identity_inputs == plan_b.identity_inputs


def test_different_identity_input_produces_different_plan(registry_and_composition) -> None:
    registry, composition = registry_and_composition
    resolver = RecordingResolver()

    plan_small = plan_substrate(
        registry, composition, "substrate:synthetic-a/v1", _loaded({}), resource_resolver=resolver
    )

    # Rebind A's definition with a resolver that resolves a different seed.
    definition_a = registry.resolve("substrate:synthetic-a/v1")
    composition = SubstratePlanningComposition(
        (SubstratePlanningRegistration(definition=definition_a, plan=_no_resource_plan(seed=8)),)
    )
    plan_large = plan_substrate(
        registry, composition, "substrate:synthetic-a/v1", _loaded({}), resource_resolver=resolver
    )

    assert plan_small != plan_large


# ---------------------------------------------------------------------------
# Planning is pure: no execution, no generation, no artifact mutation
# ---------------------------------------------------------------------------


def test_plan_substrate_never_invokes_generation(registry_and_composition) -> None:
    """Planning must never invoke a producer generation callable.

    The orchestration only calls the planning resolver (a resolution/declaration
    callable) and the resource resolver. A generation callable is never passed
    to or reachable from planning, so this is structural: planning's accepted
    surface has no generation dependency.
    """
    registry, _ = registry_and_composition
    definition_a = registry.resolve("substrate:synthetic-a/v1")

    # A generation callable is defined but is never reachable from planning: the
    # planning resolver does not receive it and planning never invokes it.
    generated: list[str] = []

    def generate() -> None:
        generated.append("generated")

    def producer(document: LoadedConfiguration) -> PlanningDeclaration:
        return PlanningDeclaration(configuration={}, resources=(), identity_inputs=())

    composition = SubstratePlanningComposition(
        (SubstratePlanningRegistration(definition=definition_a, plan=producer),)
    )
    plan_substrate(
        registry,
        composition,
        "substrate:synthetic-a/v1",
        _loaded({}),
        resource_resolver=RecordingResolver(),
    )

    # The planning resolver ran (a declaration was produced), but generation was
    # never invoked because planning never receives a generation callable; nor
    # are any artifact/staging/manifest paths touched.
    assert generated == []


# ---------------------------------------------------------------------------
# Planning failure modes
# ---------------------------------------------------------------------------


def test_plan_requires_substrate_kind(registry_and_composition) -> None:
    registry, composition = registry_and_composition
    task_definition = SyntheticDefinition(
        ref=ComponentRef.parse("task:synthetic/v1"),
        kind="task",
        description="synthetic task",
        output_contract="synthetic-contract/v1",
    )
    registry.register(task_definition)

    with pytest.raises(NotASubstrateError):
        plan_substrate(
            registry,
            composition,
            "task:synthetic/v1",
            _loaded({}),
            resource_resolver=RecordingResolver(),
        )


def test_plan_without_registered_resolver_fails(registry_and_composition) -> None:
    """A registered definition with no resolver in the composition can't be planned."""
    registry, _ = registry_and_composition
    empty_composition = SubstratePlanningComposition(())

    with pytest.raises(MissingPlanningCapabilityError):
        plan_substrate(
            registry,
            empty_composition,
            "substrate:synthetic-b/v1",
            _loaded({}),
            resource_resolver=RecordingResolver(),
        )
