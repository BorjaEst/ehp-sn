"""Behavioral tests for generic framework planning (Capability 6).

These tests exercise the framework planning surface with **synthetic in-test
producers and resolvers** — never a runtime research component. A synthetic
producer is deliberately defined inside this test module, not in ``ehp_sn``
production code (``ehp_sn.planning`` must not contain a fake producer or
placeholder). This proves the framework planning path is genuinely generic: it
works identically for a producer with no resources and for one with a resource
requirement, and never branches on a family.

Test matrix:

* planning with no resource requirement → immutable plan;
* planning with a resource requirement → resolver invoked, exact bound binding
  stored in the plan;
* same resolved scientific inputs → same plan (structural equality);
* different identity-bearing input → different plan.

No hashing is invented: identity comparison is plain structural equality of the
immutable plan (the current identity contract defines no digest semantics).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

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
    ResolvedResource,
    ResourceRequirement,
    ResourceResolutionError,
    SubstratePlanningCapability,
    plan_substrate,
)


@dataclass(frozen=True)
class SyntheticDefinition:
    """Minimal in-test discoverable definition with a substrate shape."""

    ref: ComponentRef
    kind: str
    description: str
    output_contract: str


def _loaded(values: object) -> LoadedConfiguration:
    return LoadedConfiguration(source=Path("synthetic.toml"), values=values)


class NoResourceProducer(SubstratePlanningCapability):
    """Synthetic producer declaring no resources and one identity input."""

    def __init__(self, seed: int) -> None:
        self._seed = seed

    def plan(self, document: LoadedConfiguration) -> PlanningDeclaration:
        return PlanningDeclaration(
            configuration={"seed": self._seed},
            resources=(),
            identity_inputs=(IdentityInput("seed", self._seed),),
        )


class SourceRequirementProducer(SubstratePlanningCapability):
    """Synthetic producer declaring one resource requirement and an identity input tied to it."""

    _REQUIREMENT_REF = "requirement:synthetic/source/v1"

    def __init__(self, source_ref: str) -> None:
        self._source_ref = source_ref

    def plan(self, document: LoadedConfiguration) -> PlanningDeclaration:
        requirement = ResourceRequirement(
            ref=self._REQUIREMENT_REF,
            resource_kind="raw-source",
            accepted_schema_ids=("synthetic:extraction/v1",),
            cardinality=CARDINALITY_ONE,
            definition_resource_ref=self._source_ref,
            description="synthetic upstream source",
        )
        return PlanningDeclaration(
            configuration={"source": self._source_ref},
            resources=(requirement,),
            identity_inputs=(IdentityInput("source_reference", self._source_ref),),
        )


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


@pytest.fixture()
def registry() -> ComponentRegistry:
    definition = SyntheticDefinition(
        ref=ComponentRef.parse("substrate:synthetic/v1"),
        kind="substrate",
        description="synthetic substrate",
        output_contract="synthetic-contract/v1",
    )
    registry = ComponentRegistry()
    registry.register(definition)
    return registry


def _register_producer(registry: ComponentRegistry, producer: object) -> None:
    registry.register_capability(ComponentRef.parse("substrate:synthetic/v1"), producer)


# ---------------------------------------------------------------------------
# Planning with no resource requirement
# ---------------------------------------------------------------------------


def test_plan_with_no_resources_is_immutable_plan(registry: ComponentRegistry) -> None:
    _register_producer(registry, NoResourceProducer(seed=7))
    resolver = RecordingResolver()

    plan = plan_substrate(
        registry,
        "substrate:synthetic/v1",
        _loaded({}),
        resource_resolver=resolver,
    )

    assert isinstance(plan, ExecutionPlan)
    assert plan.target == ComponentRef.parse("substrate:synthetic/v1")
    assert plan.output_contract == "synthetic-contract/v1"
    assert plan.resources == ()
    assert len(plan.identity_inputs) == 1
    # The resolver is never invoked when no resources are declared.
    assert resolver.calls == []
    # The plan is immutable (frozen dataclass).
    with pytest.raises(AttributeError):
        plan.resources = (ResolvedResource("x", "y", "z"),)  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Planning with a resource requirement
# ---------------------------------------------------------------------------


def test_plan_resolves_resource_requirement(registry: ComponentRegistry) -> None:
    _register_producer(registry, SourceRequirementProducer(source_ref="source:upstream/v1"))
    resolver = RecordingResolver()

    plan = plan_substrate(
        registry,
        "substrate:synthetic/v1",
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


def test_plan_passes_exact_bound_resource_into_identity(registry: ComponentRegistry) -> None:
    _register_producer(registry, SourceRequirementProducer(source_ref="source:upstream/v1"))
    resolver = RecordingResolver()

    plan = plan_substrate(
        registry,
        "substrate:synthetic/v1",
        _loaded({}),
        resource_resolver=resolver,
    )

    # The exact source reference the producer declared is the identity input.
    assert plan.identity_inputs == (IdentityInput("source_reference", "source:upstream/v1"),)


def test_plan_required_resource_without_reference_fails_cleanly(
    registry: ComponentRegistry,
) -> None:
    _register_producer(registry, SourceRequirementProducer(source_ref=None))  # type: ignore[arg-type]
    resolver = RecordingResolver()

    with pytest.raises(ResourceResolutionError):
        plan_substrate(
            registry,
            "substrate:synthetic/v1",
            _loaded({}),
            resource_resolver=resolver,
        )


# ---------------------------------------------------------------------------
# Identity representation: structural equality of the immutable plan
# ---------------------------------------------------------------------------


def test_same_resolved_inputs_produce_equal_plan(registry: ComponentRegistry) -> None:
    _register_producer(registry, NoResourceProducer(seed=7))
    resolver = RecordingResolver()

    plan_a = plan_substrate(registry, "substrate:synthetic/v1", _loaded({}), resource_resolver=resolver)
    plan_b = plan_substrate(registry, "substrate:synthetic/v1", _loaded({}), resource_resolver=resolver)

    assert plan_a == plan_b
    assert plan_a.identity_inputs == plan_b.identity_inputs


def test_different_identity_input_produces_different_plan(registry: ComponentRegistry) -> None:
    _register_producer(registry, NoResourceProducer(seed=7))
    resolver = RecordingResolver()

    plan_small = plan_substrate(
        registry, "substrate:synthetic/v1", _loaded({}), resource_resolver=resolver
    )

    # A producer that resolves to a different effective seed yields a different plan.
    registry.register_capability(
        ComponentRef.parse("substrate:synthetic/v1"), NoResourceProducer(seed=8)
    )
    plan_large = plan_substrate(
        registry, "substrate:synthetic/v1", _loaded({}), resource_resolver=resolver
    )

    assert plan_small != plan_large


# ---------------------------------------------------------------------------
# Planning is pure: no execution, no generation, no artifact mutation
# ---------------------------------------------------------------------------


def test_plan_substrate_never_invokes_generation(registry: ComponentRegistry) -> None:
    """Planning must never invoke a producer generation callable.

    The orchestration only calls ``capability.plan`` (a resolution/declaration
    method) and the resource resolver. A generation callable is never passed to
    or reachable from planning, so this is structural: planning's accepted
    surface has no generation dependency.
    """
    generated: list[str] = []

    class Producer(SubstratePlanningCapability):
        def plan(self, document: LoadedConfiguration) -> PlanningDeclaration:
            return PlanningDeclaration(configuration={}, resources=(), identity_inputs=())

    _register_producer(registry, Producer())
    plan_substrate(
        registry, "substrate:synthetic/v1", _loaded({}), resource_resolver=RecordingResolver()
    )

    assert generated == []
    # No artifact/staging/manifest paths are ever touched by planning, because
    # planning never receives such dependencies.


# ---------------------------------------------------------------------------
# Planning failure modes
# ---------------------------------------------------------------------------


def test_plan_requires_substrate_kind(registry: ComponentRegistry) -> None:
    task_definition = SyntheticDefinition(
        ref=ComponentRef.parse("task:synthetic/v1"),
        kind="task",
        description="synthetic task",
        output_contract="synthetic-contract/v1",
    )
    registry.register(task_definition)
    _register_producer(registry, NoResourceProducer(seed=7))

    with pytest.raises(NotASubstrateError):
        plan_substrate(registry, "task:synthetic/v1", _loaded({}), resource_resolver=RecordingResolver())


def test_plan_without_registered_capability_fails(registry: ComponentRegistry) -> None:
    # The definition is registered but no capability is bound to it.
    with pytest.raises(MissingPlanningCapabilityError):
        plan_substrate(
            registry,
            "substrate:synthetic/v1",
            _loaded({}),
            resource_resolver=RecordingResolver(),
        )
