"""Behavioral tests for the generic substrate build execution boundary (Cap 9).

These tests exercise the framework execution surface with **synthetic in-test
producers and definitions** — never a runtime research component. A synthetic
producer is deliberately defined inside this test module, not in ``ehp_sn``
production code (``ehp_sn.execution`` must not contain a fake producer or
placeholder). This proves the framework execution path is genuinely generic: the
same orchestration runs materially different producer shapes without a family
branch.

The synthetic producers encode the structural diversity demonstrated by the four
authoritative substrate specifications (``docs/docs/research/substrates/``):

* **producer A** — procedural records with an intrinsic split descriptor
  (shaped after Dagflow: ``simple-digraph``-style records, no upstream resource);
* **producer B** — complete categorical fields with **no split** and an auxiliary
  domain/vocabulary logical resource (shaped after ObsField:
  ``categorical-field``-style complete realizations);
* **producer C** — source import with collection-level deduplication and a
  separate complete lineage resource (shaped after Maze-ND: ``raster-topology``
  + many-to-one source lineage); the producer performs the scientific loop
  itself, so the framework never assumes record-at-a-time output;
* **producer D** — rejection/retry with acceptance and **no split** (shaped after
  DungeonGen: a candidate is either accepted or rejected under a retry budget).

Each producer registers an execution operation for a distinct synthetic
definition, and all four run through the *same* :func:`execute_substrate`
without any family names, raster assumptions, mandatory split, topology
assumption, record-at-a-time assumption, or source/procedural assumption.

The test matrix also covers the framework invariants:

* a plan is consumed exactly once — execution never re-resolves config or
  reselects resources (the session carries the plan's bound values as-is);
* ``record_id`` is derived by the framework, is deterministic, order-independent,
  and distinct from plan identity;
* the materialization is **uncommitted** — no release coordinate and no final
  artifact are produced;
* a ready plan without a bound execution operation is a controlled
  :class:`MissingExecutionCapabilityError`;
* a plan for a non-substrate target is a controlled
  :class:`ExecutionValidationError`.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from ehp_sn.configuration import LoadedConfiguration
from ehp_sn.discovery import ComponentRegistry
from ehp_sn.execution import (
    ExecutionValidationError,
    GeneratedRecordBody,
    MaterializationSession,
    MissingExecutionCapabilityError,
    PlanValidationReport,
    RealizationKey,
    SubstrateExecutionComposition,
    SubstrateExecutionRegistration,
    derive_record_id,
    execute_substrate,
)
from ehp_sn.experiments import ComponentRef
from ehp_sn.planning import (
    ExecutionPlan,
    IdentityInput,
    PlanningDeclaration,
    PlanningResolver,
    ResourceRequirement,
    SubstratePlanningComposition,
    SubstratePlanningRegistration,
    plan_substrate,
)


#: A resource resolver that binds any requirement to its declared reference.
def _binding_resolver(requirement: ResourceRequirement):
    from ehp_sn.planning import ResourceResolutionError

    if requirement.definition_resource_ref is None:
        raise ResourceResolutionError(f"no declared reference for {requirement.ref!r}")
    from ehp_sn.planning import ResolvedResource

    return ResolvedResource(
        requirement_ref=requirement.ref,
        resource_ref=requirement.definition_resource_ref,
        resolution_source="definition",
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


def _single_identity_plan(name: str, value: Any) -> PlanningResolver:
    """A planning resolver declaring one identity input and no resources."""

    def plan(document: LoadedConfiguration) -> PlanningDeclaration:
        return PlanningDeclaration(
            configuration={"value": value},
            resources=(),
            identity_inputs=(IdentityInput(name, value),),
        )

    return plan


def _register_definition(
    registry: ComponentRegistry,
    *,
    ref: str,
    output_contract: str,
) -> SyntheticDefinition:
    component_ref = ComponentRef.parse(ref)
    definition = SyntheticDefinition(
        ref=component_ref,
        kind="substrate",
        description=f"synthetic {component_ref.name}",
        output_contract=output_contract,
    )
    registry.register(definition)
    return definition


def _build_plan(
    registry: ComponentRegistry,
    definition: SyntheticDefinition,
    planning: PlanningResolver,
) -> ExecutionPlan:
    composition = SubstratePlanningComposition(
        (SubstratePlanningRegistration(definition=definition, plan=planning),)
    )
    return plan_substrate(
        registry,
        composition,
        definition.ref,
        _loaded({"seed": 7}),
        resource_resolver=_binding_resolver,
    )


# ---------------------------------------------------------------------------
# Producer A — procedural records with an intrinsic split descriptor
# (shaped after Dagflow: no upstream resource, intrinsic split).
# ---------------------------------------------------------------------------


def _producer_a(session: MaterializationSession) -> None:
    """Generate a few records, each carrying an intrinsic split descriptor."""
    for split in ("train", "validation", "test"):
        for index in range(1, 3):
            session.add_record(
                GeneratedRecordBody(
                    content={"nodes": 4, "index": index},
                    realization_key=RealizationKey(
                        inputs=(
                            IdentityInput("split", split),
                            IdentityInput("realization_index", index),
                        )
                    ),
                    descriptors=(IdentityInput("split", split),),
                )
            )


# ---------------------------------------------------------------------------
# Producer B — complete categorical fields, no split, auxiliary domain resource
# (shaped after ObsField: no split, domain/vocabulary through logical resources).
# ---------------------------------------------------------------------------


def _producer_b(session: MaterializationSession) -> None:
    """Generate complete fields with no split and add a domain declaration."""
    session.add_logical_resource(
        "domain", {"kind": "ambient-domain/v1", "states": 9}, resource_kind="domain"
    )
    for index in range(1, 4):
        session.add_record(
            GeneratedRecordBody(
                content={"value_kind": "categorical", "index": index},
                realization_key=RealizationKey(inputs=(IdentityInput("realization_index", index),)),
                descriptors=(),
            )
        )


# ---------------------------------------------------------------------------
# Producer C — source import, collection-level deduplication, lineage resource
# (shaped after Maze-ND: many source rows -> fewer unique topology records plus
# a separate complete lineage mapping resource).
# ---------------------------------------------------------------------------


def _producer_c(session: MaterializationSession) -> None:
    """Deduplicate source rows into unique records and add a lineage resource.

    This producer performs the *scientific inner loop itself* (source-wide
    normalisation then dedup), demonstrating that framework execution does not
    force record-at-a-time generation. Two identical source rows collapse to one
    record, and a separate complete lineage resource records the many-to-one map.
    """
    source_rows = [
        {"raster": "AA", "row_id": "r1"},
        {"raster": "AB", "row_id": "r2"},
        {"raster": "AA", "row_id": "r3"},  # duplicate of r1 -> same record
    ]
    seen: dict[str, str] = {}  # canonical content -> record_id
    lineage: list[dict[str, str]] = []
    for row in source_rows:
        canonical = row["raster"]
        if canonical not in seen:
            record = session.add_record(
                GeneratedRecordBody(
                    content={"extent": [1, 2], "passable": list(canonical)},
                    realization_key=RealizationKey(
                        inputs=(IdentityInput("canonical_topology", canonical),)
                    ),
                    descriptors=(),
                )
            )
            seen[canonical] = record.record_id
        lineage.append({"source_row": row["row_id"], "record_id": seen[canonical]})

    session.add_logical_resource("complete-source-lineage", {"rows": lineage}, resource_kind="lineage")


# ---------------------------------------------------------------------------
# Producer D — rejection/retry then acceptance, no split
# (shaped after DungeonGen: a candidate is accepted only after retries; no split).
# ---------------------------------------------------------------------------


def _producer_d(session: MaterializationSession) -> None:
    """Accept records only after rejecting invalid candidates under a budget.

    The candidate value must be even; odd candidates are rejected and retried
    with the next index. This demonstrates retry/acceptance living in the
    producer, not in framework execution, and that framework execution does not
    assume every generated candidate becomes a record.
    """
    budget = 20
    accepted = 0
    candidate = 0
    while accepted < 3 and candidate < budget:
        if candidate % 2 == 0:
            session.add_record(
                GeneratedRecordBody(
                    content={"accepted": candidate},
                    realization_key=RealizationKey(
                        inputs=(IdentityInput("logical_topology_index", accepted),)
                    ),
                    descriptors=(IdentityInput("attempts", candidate),),
                )
            )
            accepted += 1
        candidate += 1


# ---------------------------------------------------------------------------
# Shared orchestration: each producer runs through the same execute_substrate.
# ---------------------------------------------------------------------------


def _run(
    registry: ComponentRegistry,
    definition: SyntheticDefinition,
    producer: Callable[[MaterializationSession], None],
    plan: ExecutionPlan,
):
    execution_composition = SubstrateExecutionComposition(
        (SubstrateExecutionRegistration(definition=definition, execute=producer),)
    )
    return execute_substrate(registry, execution_composition, plan)


def test_producer_a_procedural_intrinsic_split() -> None:
    """A procedural producer with intrinsic splits completes through the boundary."""
    registry = ComponentRegistry()
    definition = _register_definition(
        registry, ref="substrate:synthetic-a/v1", output_contract="simple-digraph/v1"
    )
    plan = _build_plan(registry, definition, _single_identity_plan("seed", 7))

    result = _run(registry, definition, _producer_a, plan)

    assert result.report.ready is True
    assert len(result.materialization.records) == 6  # 3 splits x 2
    assert len(result.materialization.logical_resources) == 0
    # Intrinsic split is a producer descriptor, materialized opaquely alongside
    # the record, not a framework-owned structure.
    splits = {r for rec in result.materialization.records for r in _split_of(rec)}
    assert splits == {"train", "validation", "test"}
    # record_ids are unique and framework-derived.
    ids = [rec.record_id for rec in result.materialization.records]
    assert len(set(ids)) == len(ids)
    assert all(rec.schema_ref == "simple-digraph/v1" for rec in result.materialization.records)


def _split_of(record) -> set[str]:
    """Read the intrinsic split descriptor a producer attached to a record."""
    from ehp_sn.execution import LogicalRecord

    values = {d.name: d.value for d in record.descriptors} if isinstance(record, LogicalRecord) else {}
    return {values["split"]} if "split" in values else set()


def test_producer_b_categorical_no_split_aux_resource() -> None:
    """A complete-field producer with no split and an auxiliary domain resource."""
    registry = ComponentRegistry()
    definition = _register_definition(
        registry, ref="substrate:synthetic-b/v1", output_contract="categorical-field/v1"
    )
    plan = _build_plan(registry, definition, _single_identity_plan("domain", "ambient-domain/v1"))

    result = _run(registry, definition, _producer_b, plan)

    assert result.report.ready is True
    assert len(result.materialization.records) == 3
    # No split descriptors anywhere.
    assert all(rec.descriptors == () for rec in result.materialization.records)
    # Auxiliary domain resource is present as framework logical content.
    resources = {res.name: res for res in result.materialization.logical_resources}
    assert resources["domain"].resource_kind == "domain"
    # The session carries the plan's opaque configuration and bound resources
    # without re-resolution.
    assert result.materialization.configuration == {"value": "ambient-domain/v1"}


def test_producer_c_source_import_dedup_lineage() -> None:
    """A source-import producer collapses duplicates and adds a lineage resource."""
    registry = ComponentRegistry()
    definition = _register_definition(
        registry, ref="substrate:synthetic-c/v1", output_contract="raster-topology/v1"
    )
    plan = _build_plan(registry, definition, _single_identity_plan("source_reference", "src://maze/v7"))

    result = _run(registry, definition, _producer_c, plan)

    # Two unique rasters -> two records (the duplicate source row collapsed).
    assert len(result.materialization.records) == 2
    # A separate complete lineage resource records all three source rows.
    lineage = next(
        res for res in result.materialization.logical_resources if res.name == "complete-source-lineage"
    )
    assert lineage.resource_kind == "lineage"
    rows = lineage.content["rows"]
    assert len(rows) == 3
    # Both duplicate rows resolve to the same record_id.
    assert rows[0]["record_id"] == rows[2]["record_id"]
    assert rows[0]["record_id"] != rows[1]["record_id"]
    # The session exposes the bound resources exactly as planned (identity lookup
    # only; no independent resource reselection by execution).
    assert result.materialization.resources == ()


def test_producer_d_retry_acceptance_no_split() -> None:
    """A retry/acceptance producer with no split completes through the boundary.

    The producer rejects odd candidates; framework execution never sees the
    rejects and never assumes every generated candidate becomes a record.
    """
    registry = ComponentRegistry()
    definition = _register_definition(
        registry, ref="substrate:synthetic-d/v1", output_contract="raster-topology/v1"
    )
    plan = _build_plan(registry, definition, _single_identity_plan("generator_revision", "dungeon/v2"))

    result = _run(registry, definition, _producer_d, plan)

    assert result.report.ready is True
    assert len(result.materialization.records) == 3  # only accepted records
    assert all(rec.content["accepted"] % 2 == 0 for rec in result.materialization.records)
    assert all(
        rec.descriptors == () or rec.descriptors[0].name == "attempts"
        for rec in result.materialization.records
    )


def test_same_plan_consumed_once_no_reresolution() -> None:
    """The plan is consumed exactly once; execution never re-resolves config.

    The materialization session carries the plan's opaque configuration and
    exact bound resources unchanged, so a producer cannot make a second
    scientific selection after planning.
    """
    registry = ComponentRegistry()
    definition = _register_definition(
        registry, ref="substrate:synthetic-a/v1", output_contract="simple-digraph/v1"
    )
    plan = _build_plan(registry, definition, _single_identity_plan("seed", 7))

    result = _run(registry, definition, _producer_a, plan)

    assert result.materialization.configuration == {"value": 7}
    assert result.materialization.identity_inputs == (IdentityInput("seed", 7),)
    assert result.materialization.component == definition.ref


def test_record_id_framework_derived_and_plan_independent() -> None:
    """record_id is framework-derived and independent of plan identity."""
    registry = ComponentRegistry()
    definition = _register_definition(
        registry, ref="substrate:synthetic-a/v1", output_contract="simple-digraph/v1"
    )
    key = RealizationKey(inputs=(IdentityInput("split", "train"), IdentityInput("realization_index", 1)))

    record_id = derive_record_id(definition.ref.canonical, "simple-digraph/v1", key)

    # Deterministic.
    assert record_id == derive_record_id(definition.ref.canonical, "simple-digraph/v1", key)
    # Changing component, schema, or realization key changes the identifier.
    assert record_id != derive_record_id("substrate:other/v1", "simple-digraph/v1", key)
    assert record_id != derive_record_id(definition.ref.canonical, "raster-topology/v1", key)
    assert record_id != derive_record_id(
        definition.ref.canonical,
        "simple-digraph/v1",
        RealizationKey(inputs=(IdentityInput("split", "test"), IdentityInput("realization_index", 1))),
    )
    # It is not derived from plan identity (plan identity includes split counts,
    # which must not change an existing realization's record_id).
    plan_id = result_plan_id(registry, definition)
    assert plan_id != record_id


def result_plan_id(registry: ComponentRegistry, definition: SyntheticDefinition) -> str:
    from ehp_sn.planning import plan_identity

    plan = _build_plan(registry, definition, _single_identity_plan("seed", 7))
    return plan_identity(plan)


def test_record_id_unique_within_artifact_duplicate_raises() -> None:
    """Registering the same realization key twice is a controlled duplicate error."""
    registry = ComponentRegistry()
    definition = _register_definition(
        registry, ref="substrate:synthetic-a/v1", output_contract="simple-digraph/v1"
    )
    session = MaterializationSession.from_plan(
        _build_plan(registry, definition, _single_identity_plan("seed", 7))
    )
    body = GeneratedRecordBody(
        content={"nodes": 4},
        realization_key=RealizationKey(inputs=(IdentityInput("realization_index", 1),)),
    )
    session.add_record(body)
    with pytest.raises(ValueError, match="duplicate record_id"):
        session.add_record(body)


def test_missing_execution_capability_is_controlled() -> None:
    """A ready plan without a bound execution operation is a controlled error."""
    registry = ComponentRegistry()
    definition = _register_definition(
        registry, ref="substrate:synthetic-a/v1", output_contract="simple-digraph/v1"
    )
    plan = _build_plan(registry, definition, _single_identity_plan("seed", 7))
    # Composition deliberately bound to a different (unused) definition.
    other = _register_definition(
        registry, ref="substrate:unused/v1", output_contract="simple-digraph/v1"
    )
    empty = SubstrateExecutionComposition(
        (SubstrateExecutionRegistration(definition=other, execute=_producer_a),)
    )
    with pytest.raises(MissingExecutionCapabilityError):
        execute_substrate(registry, empty, plan)


def test_non_substrate_plan_is_execution_validation_error() -> None:
    """Execution refuses a plan whose target resolves to a non-substrate.

    The plan is constructed directly (not through ``plan_substrate``, which would
    reject the target earlier); execution re-resolves the target and rejects it
    at readiness time via a controlled :class:`ExecutionValidationError`.
    """
    registry = ComponentRegistry()
    task_ref = ComponentRef.parse("task:synthetic/v1")
    definition = SyntheticDefinition(
        ref=task_ref, kind="task", description="a task", output_contract="corpus/v1"
    )
    registry.register(definition)

    plan = ExecutionPlan(
        target=task_ref,
        output_contract="corpus/v1",
        configuration={"value": 1},
        resources=(),
        identity_inputs=(IdentityInput("seed", 1),),
    )
    execution_composition = SubstrateExecutionComposition(
        (SubstrateExecutionRegistration(definition=definition, execute=lambda s: None),)
    )
    with pytest.raises(ExecutionValidationError):
        execute_substrate(registry, execution_composition, plan)


def test_validation_report_references_stable_plan_id() -> None:
    """The validation report carries a stable plan identity for later stages."""
    registry = ComponentRegistry()
    definition = _register_definition(
        registry, ref="substrate:synthetic-a/v1", output_contract="simple-digraph/v1"
    )
    plan = _build_plan(registry, definition, _single_identity_plan("seed", 7))
    result = _run(registry, definition, _producer_a, plan)

    report: PlanValidationReport = result.report
    assert report.ready is True
    assert report.plan_id == result.plan_id
    assert report.plan_id.startswith("sha256:")
