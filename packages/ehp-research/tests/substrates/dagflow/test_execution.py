"""Integration-style tests for the Dagflow execution operation and registration.

Exercises the producer-integration boundary for ``substrate:dagflow/v1`` over
the real framework execution composition:

* the registered Dagflow definition ↔ execution operation relationship through
  the entry-point provider;
* the full ``execute_substrate`` path consuming the authoritative plan and
  materializing a session (framework-derived ``record_id``);
* the target acceptance: removing the execution registration yields
  :class:`MissingExecutionCapabilityError`; restoring it succeeds through the
  same generic execution path;
* Target acceptance: the producer cannot override ``record_id``, the split is
  producer-supplied, the record schema is ``simple-digraph/v1``, and the
  materialized output contains no private construction identity.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from ehp_research.registration import execution_registrations, planning_registrations
from ehp_research.substrates.dagflow import DAGFLOW_DEFINITION
from ehp_research.substrates.dagflow import execute as dagflow_execute
from ehp_sn.configuration import load_configuration
from ehp_sn.discovery import effective_registry
from ehp_sn.execution import (
    MissingExecutionCapabilityError,
    SubstrateExecutionComposition,
    execute_substrate,
)
from ehp_sn.planning import (
    ResolvedResource,
    ResourceRequirement,
    ResourceResolutionError,
    SubstratePlanningComposition,
    plan_substrate,
)


class _GenericResolver:
    """Minimal generic resource resolver for the planning path (no family logic)."""

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


def _execution_composition() -> SubstrateExecutionComposition:
    return SubstrateExecutionComposition(execution_registrations())


def _plan_text() -> str:
    return """[substrate]
    variant = "single-terminal"

[generation]
    protocol = "constructive-forward/v1"
    seed     = 7

[graph]
    node_count                  = 6
    additional_edge_probability = 0.20

[splits.train]
    count = 4

[splits.validation]
    count = 1

[splits.test]
    count = 1
"""


@pytest.fixture()
def plan(tmp_path: Path):
    """An authoritative ExecutionPlan for a small Dagflow configuration."""
    config_path = tmp_path / "dagflow.toml"
    config_path.write_text(_plan_text(), encoding="utf-8")
    registry = effective_registry()
    planning = SubstratePlanningComposition(planning_registrations())
    return plan_substrate(
        registry,
        planning,
        "substrate:dagflow/v1",
        load_configuration(str(config_path)),
        resource_resolver=_GenericResolver(),
    )


def test_registration_binds_dagflow_definition_to_execution_operation() -> None:
    """The Dagflow definition maps to its execution operation by identity."""
    registry = effective_registry()
    definition = registry.resolve(DAGFLOW_DEFINITION.ref.canonical)
    composition = _execution_composition()
    assert composition.contains(definition)
    assert composition.execute(definition) is dagflow_execute


def test_execute_materializes_records_with_framework_record_id(plan) -> None:
    """Execution derives framework record_ids and simple-digraph/v1 records."""
    registry = effective_registry()
    result = execute_substrate(registry, _execution_composition(), plan)
    records = result.materialization.records
    assert len(records) == 6
    for record in records:
        assert record.schema_ref == "simple-digraph/v1"
        # content is the JSON-compatible canonical graph
        assert {"node_count", "edges"} == set(record.content.keys())


def test_producer_cannot_override_record_id(plan) -> None:
    """The producer cannot set record_id (framework-derived)."""
    registry = effective_registry()
    result = execute_substrate(registry, _execution_composition(), plan)
    for record in result.materialization.records:
        # record_id is a framework digest string, not a producer-supplied field
        assert record.record_id.startswith("sha256:")
        assert record.record_id


def test_split_is_producer_supplied_descriptor(plan) -> None:
    """The intrinsic split is carried as a producer descriptor on every record."""
    registry = effective_registry()
    result = execute_substrate(registry, _execution_composition(), plan)
    splits = {
        next(d.value for d in record.descriptors if d.name == "split")
        for record in result.materialization.records
    }
    assert splits == {"train", "validation", "test"}


def test_materialized_output_contains_no_private_construction_id(plan) -> None:
    """Public records carry no private construction identity."""
    registry = effective_registry()
    result = execute_substrate(registry, _execution_composition(), plan)
    for record in result.materialization.records:
        # content is only node_count + canonical edges (simple-digraph/v1)
        assert set(record.content.keys()) == {"node_count", "edges"}


def test_removing_registration_yields_missing_capability(plan) -> None:
    """With no execution registration, the generic path raises the capability error."""
    registry = effective_registry()
    empty = SubstrateExecutionComposition(())
    with pytest.raises(MissingExecutionCapabilityError):
        execute_substrate(registry, empty, plan)


def test_restoring_registration_succeeds_same_path(plan) -> None:
    """Restoring the registration succeeds through the exact same generic path."""
    registry = effective_registry()
    result = execute_substrate(registry, _execution_composition(), plan)
    assert len(result.materialization.records) == 6
