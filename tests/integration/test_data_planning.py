"""Integration tests — the complete cross-package data-build planning path.

This is where ``ehp_sn`` and ``ehp_research`` meet for planning (root-level
integration scope). It proves the production composition path end to end:

    registered Dagflow / Maze-ND definitions      (discovery registry)
    producer planning resolvers                   (planning composition)
        ↓
    generic ehp_sn plan_substrate (injected composition)
        ↓  (generic resource resolver)
    immutable framework ExecutionPlan

Discovery and planning composition are distinct concerns installed at bootstrap:
``effective_registry`` provides definitions; the planning composition provides
each definition's producer planning resolver, selected by definition identity.
Both real providers travel through the **same** generic orchestration function;
there is no Dagflow-specific or Maze-ND-specific branch inside ``ehp_sn``.

Expected metadata is **derived from the registered authoritative definitions**
and the real resolved configurations (via the composed planning resolvers), not
from a second hard-coded catalogue.

The resource resolver used here is a minimal in-test resolver for the Maze-ND
source requirement (the immutable source binding step, which the framework
documentation defers to the resource subsystem). It is deliberately generic:
it binds any requirement with a declared exact reference; it has no family
logic.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from ehp_research.registration import planning_registrations
from ehp_research.substrates.dagflow import DAGFLOW_DEFINITION
from ehp_research.substrates.maze_nd import MAZE_ND_DEFINITION
from ehp_sn.configuration import load_configuration
from ehp_sn.discovery import effective_registry
from ehp_sn.planning import (
    ExecutionPlan,
    ResolvedResource,
    ResourceRequirement,
    ResourceResolutionError,
    SubstratePlanningComposition,
    plan_substrate,
)

#: Repo root, located relative to this test file (…/tests/integration/ → repo).
_REPO_ROOT = Path(__file__).resolve().parents[2]
_DAGFLOW_PROFILE = _REPO_ROOT / "config" / "data" / "dagflow" / "constructive-dense.toml"
_MAZE_ND_PROFILE = _REPO_ROOT / "config" / "data" / "maze-nd" / "connected-source.toml"


class _GenericResolver:
    """Minimal in-test generic resource resolver.

    Binds any requirement that declares an exact logical reference; fails
    cleanly when a required requirement has none. No family logic.
    """

    def resolve(self, requirement: ResourceRequirement) -> ResolvedResource:
        if requirement.definition_resource_ref is None:
            raise ResourceResolutionError(
                f"no exact resource reference for requirement {requirement.ref!r}"
            )
        return ResolvedResource(
            requirement_ref=requirement.ref,
            resource_ref=requirement.definition_resource_ref,
            resolution_source="definition",
        )


@pytest.fixture()
def registry_and_composition():
    """The production bootstrap: effective registry + composed planning resolvers."""
    registry = effective_registry()
    composition = SubstratePlanningComposition(planning_registrations())
    return registry, composition


def _dagflow_document():
    return load_configuration(_DAGFLOW_PROFILE)


def _maze_document():
    return load_configuration(_MAZE_ND_PROFILE)


def _plan(registry_and_composition, target: str, document):
    registry, composition = registry_and_composition
    return plan_substrate(
        registry,
        composition,
        target,
        document,
        resource_resolver=_GenericResolver(),
    )


# ---------------------------------------------------------------------------
# Dagflow: resources empty, output from definition, identity inputs present
# ---------------------------------------------------------------------------


def test_dagflow_plan_produces_immutable_plan(registry_and_composition) -> None:
    plan = _plan(registry_and_composition, "substrate:dagflow/v1", _dagflow_document())

    assert isinstance(plan, ExecutionPlan)
    # Selected component reference from the registered definition.
    assert plan.target == DAGFLOW_DEFINITION.ref
    # Expected output contract derived from the registered definition (single authority).
    assert plan.output_contract == DAGFLOW_DEFINITION.output_contract == "simple-digraph/v1"


def test_dagflow_plan_declares_no_resources(registry_and_composition) -> None:
    plan = _plan(registry_and_composition, "substrate:dagflow/v1", _dagflow_document())

    # Dagflow is procedurally generated: no external source requirement.
    assert plan.resources == ()


def test_dagflow_plan_carries_identity_inputs(registry_and_composition) -> None:
    plan = _plan(registry_and_composition, "substrate:dagflow/v1", _dagflow_document())

    names = {input_.name for input_ in plan.identity_inputs}
    # Family-specific identity inputs are declared (WHAT is identity-bearing).
    assert {"variant", "generation_protocol", "seed", "node_count_policy"} <= names
    # The effective seed from the resolved configuration is bound into identity.
    seed_input = next(i for i in plan.identity_inputs if i.name == "seed")
    assert seed_input.value == 1729


# ---------------------------------------------------------------------------
# Maze-ND: source requirement declared and bound generically
# ---------------------------------------------------------------------------


def test_maze_plan_declares_source_requirement_and_binds_it(registry_and_composition) -> None:
    plan = _plan(registry_and_composition, "substrate:maze-nd/v1", _maze_document())

    assert isinstance(plan, ExecutionPlan)
    assert plan.target == MAZE_ND_DEFINITION.ref
    assert plan.output_contract == MAZE_ND_DEFINITION.output_contract == "raster-topology/v1"

    # The upstream source is expressed as a generic bound resource requirement.
    assert len(plan.resources) == 1
    bound = plan.resources[0]
    assert bound.requirement_ref == "requirement:substrate/maze-nd-source/v1"
    # The exact source reference declared by the producer is bound.
    assert bound.resource_ref == "UNRESOLVED-EXTERNAL-SOURCE"


def test_maze_plan_carries_source_identity(registry_and_composition) -> None:
    plan = _plan(registry_and_composition, "substrate:maze-nd/v1", _maze_document())

    names = {input_.name for input_ in plan.identity_inputs}
    assert {"source_reference", "source_fingerprint", "source_schema"} <= names
    fingerprint = next(i for i in plan.identity_inputs if i.name == "source_fingerprint")
    assert fingerprint.value == "UNRESOLVED-EXTERNAL-SOURCE"


# ---------------------------------------------------------------------------
# Both providers through the same orchestration; generic plan identity
# ---------------------------------------------------------------------------


def test_both_providers_share_one_planning_path(registry_and_composition) -> None:
    dagflow = _plan(registry_and_composition, "substrate:dagflow/v1", _dagflow_document())
    maze = _plan(registry_and_composition, "substrate:maze-nd/v1", _maze_document())

    # Both are the same immutable ExecutionPlan type from the same function.
    assert isinstance(dagflow, ExecutionPlan)
    assert isinstance(maze, ExecutionPlan)
    assert type(dagflow) is type(maze)
    # Different components and inputs → different plans.
    assert dagflow != maze


def test_discovery_does_not_own_producer_resolvers(registry_and_composition) -> None:
    """The discovery registry resolves definitions only; the composition owns resolvers.

    ``registry.resolve(def.ref) is def`` for each authoritative definition, and
    the planning resolvers are selected by definition identity from the composed
    composition, not stored in the registry.
    """
    registry, composition = registry_and_composition
    assert registry.resolve(DAGFLOW_DEFINITION.ref) is DAGFLOW_DEFINITION
    assert registry.resolve(MAZE_ND_DEFINITION.ref) is MAZE_ND_DEFINITION

    # No behavioral lookup is available on the registry.
    assert not hasattr(registry, "capability")
    assert not hasattr(registry, "register_capability")

    # The composition binds resolvers by definition identity.
    assert composition.contains(DAGFLOW_DEFINITION)
    assert composition.contains(MAZE_ND_DEFINITION)
    assert composition.resolver(DAGFLOW_DEFINITION) is not None
    assert composition.resolver(MAZE_ND_DEFINITION) is not None
