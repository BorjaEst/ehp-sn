"""Integration-style tests for the ObsField execution operation and registration.

Verifies the producer-integration boundary for ``substrate:obsfield/v1`` over
the real framework execution composition: registration, the full
``execute_substrate`` path, and the acceptance that ObsField is only
registered once its supported profile is genuinely executable (no placeholder).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from ehp_research.registration import execution_registrations, planning_registrations
from ehp_research.substrates.obsfield import OBSFIELD_DEFINITION
from ehp_research.substrates.obsfield import execute as obsfield_execute
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
    """Minimal generic resource resolver (no family logic)."""

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
    variant = "categorical-complete"

[domain]
    schema = "rectangular-row-column/v1"
    height = 4
    width  = 5

[vocabulary]
    identity    = "obs-vocabulary:anonymous-3/v1"
    cardinality = 3

[assignment]
    protocol = "categorical-random/v1"

[assignment.parameters]
    distribution = "uniform"

[generation]
    seed              = 0
    realization_count = 6
"""


@pytest.fixture()
def plan(tmp_path: Path):
    config_path = tmp_path / "obsfield.toml"
    config_path.write_text(_plan_text(), encoding="utf-8")
    registry = effective_registry()
    planning = SubstratePlanningComposition(planning_registrations())
    return plan_substrate(
        registry,
        planning,
        "substrate:obsfield/v1",
        load_configuration(str(config_path)),
        resource_resolver=_GenericResolver(),
    )


def test_registration_binds_obsfield_definition_to_execution_operation() -> None:
    """The ObsField definition maps to its execution operation by identity."""
    registry = effective_registry()
    definition = registry.resolve(OBSFIELD_DEFINITION.ref.canonical)
    composition = _execution_composition()
    assert composition.contains(definition)
    assert composition.execute(definition) is obsfield_execute


def test_execute_materializes_categorical_field_records(plan) -> None:
    """Execution derives framework record_ids with categorical-field/v1 schema."""
    registry = effective_registry()
    result = execute_substrate(registry, _execution_composition(), plan)
    records = result.materialization.records
    assert len(records) == 6
    for record in records:
        assert record.schema_ref == "categorical-field/v1"
        assert set(record.content.keys()) == {"domain", "vocabulary", "observation_ids"}


def test_no_split_no_passability_no_topology(plan) -> None:
    """ObsField records carry no split, topology, or passability (Gate B)."""
    registry = effective_registry()
    result = execute_substrate(registry, _execution_composition(), plan)
    for record in result.materialization.records:
        assert record.descriptors == ()
        assert "passable" not in record.content
        assert "topology" not in record.content


def test_removing_registration_yields_missing_capability(plan) -> None:
    """With no execution registration, the generic path raises the capability error."""
    registry = effective_registry()
    empty = SubstrateExecutionComposition(())
    with pytest.raises(MissingExecutionCapabilityError):
        execute_substrate(registry, empty, plan)
