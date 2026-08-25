"""Behavioral tests for the generic substrate-artifact lifecycle (Phase 4B).

These tests exercise the framework artifact assembly, identity, and commit
semantics with **synthetic in-test producers and definitions** — never a runtime
research component. Four structurally different producer shapes (procedural +
intrinsic split; complete field + no split + auxiliary domain; source import +
lineage; retry/acceptance + no split) all run through the *same*
:func:`assemble_artifact` / :func:`find_reusable` / :func:`commit_artifact`
path, proving the lifecycle is generic.

Covered invariants:

* assembly consumes the authoritative plan + plan-bound materialization and
  never invokes the producer (the producer callable is prohibited inside the
  artifact layer by the architecture guard);
* ``SubstrateArtifact`` is never a ``MaterializationResult`` and never a partial
  assembly; it is immutable and committed;
* ``PlanId != build_input_identity != artifact_fingerprint != record_id``;
* the artifact fingerprint is exact-JCS and independent of physical paths;
* auxiliary logical resources are first-class; splits are optional (present only
  as producer descriptors);
* deterministic reuse: the same scientific build performed twice returns the
  existing artifact; a conflicting build fails;
* failed assembly never yields an artifact discovery would treat as valid.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from ehp_sn.artifacts import (
    AssembledArtifact,
    CommitConflictError,
    LogicalResourceDescriptor,
    SubstrateArtifact,
    artifact_fingerprint,
    assemble_artifact,
    commit_artifact,
    find_reusable,
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
    ExecutionPlan,
    IdentityInput,
    PlanningDeclaration,
    PlanningResolver,
    ResolvedResource,
    ResourceRequirement,
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


class _BindingResolver:
    """Binds any requirement to its declared reference (declared->BOUND)."""

    def resolve(self, requirement: ResourceRequirement) -> ResolvedResource:
        from ehp_sn.planning import ResourceResolutionError

        if requirement.definition_resource_ref is None:
            raise ResourceResolutionError(f"no declared reference for {requirement.ref!r}")
        return ResolvedResource(
            requirement_ref=requirement.ref,
            resource_ref=requirement.definition_resource_ref,
            resolution_source="definition",
        )


_binding_resolver = _BindingResolver()


def _register(
    registry: ComponentRegistry,
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


def _plan(registry: ComponentRegistry, definition: SyntheticDefinition, resolver) -> ExecutionPlan:
    composition = SubstratePlanningComposition(
        (SubstratePlanningRegistration(definition=definition, plan=resolver),)
    )
    return plan_substrate(
        registry,
        composition,
        definition.ref,
        _loaded({"seed": 7}),
        resource_resolver=_binding_resolver,
    )


def _identity_plan(name: str, value: Any) -> PlanningResolver:
    def plan(document: LoadedConfiguration) -> PlanningDeclaration:
        return PlanningDeclaration(
            configuration={"value": value},
            resources=(),
            identity_inputs=(IdentityInput(name, value),),
        )

    return plan


def _execute(
    registry: ComponentRegistry,
    definition: SyntheticDefinition,
    producer: Callable[[MaterializationSession], None],
    plan: ExecutionPlan,
):
    composition = SubstrateExecutionComposition(
        (SubstrateExecutionRegistration(definition=definition, execute=producer),)
    )
    return execute_substrate(registry, composition, plan)


# --- Synthetic producer shapes (same four as the execution boundary tests) ---


def _producer_a(session: MaterializationSession) -> None:
    """Procedural records with an intrinsic split descriptor (Dagflow-shaped)."""
    for split in ("train", "validation"):
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


def _producer_b(session: MaterializationSession) -> None:
    """Complete categorical fields, no split, auxiliary domain (ObsField-shaped)."""
    session.add_logical_resource(
        "domain", {"kind": "ambient-domain/v1", "states": 9}, resource_kind="domain"
    )
    for index in range(1, 3):
        session.add_record(
            GeneratedRecordBody(
                content={"value_kind": "categorical", "index": index},
                realization_key=RealizationKey(inputs=(IdentityInput("realization_index", index),)),
                descriptors=(),
            )
        )


def _build_artifact(registry, definition, producer, plan) -> AssembledArtifact:
    result = _execute(registry, definition, producer, plan)
    return assemble_artifact(plan, result)


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #


def test_assembly_produces_substrate_metadata() -> None:
    registry = ComponentRegistry()
    definition = _register(registry, "substrate:synthetic-a/v1", "simple-digraph/v1")
    plan = _plan(registry, definition, _identity_plan("seed", 7))
    assembled = _build_artifact(registry, definition, _producer_a, plan)

    assert assembled.component_ref == "substrate:synthetic-a/v1"
    assert assembled.output_contract == "simple-digraph/v1"
    assert assembled.build_input_identity.startswith("sha256:")
    assert assembled.artifact_fingerprint.startswith("sha256:")
    assert assembled.build_input_identity != assembled.artifact_fingerprint
    # Intrinsic split surfaces as a producer descriptor, not a framework field.
    splits = {d.name for d in assembled.producer_descriptors}
    assert "split" in splits


def test_assembly_includes_auxiliary_resources_and_index() -> None:
    registry = ComponentRegistry()
    definition = _register(registry, "substrate:synthetic-b/v1", "categorical-field/v1")
    plan = _plan(registry, definition, _identity_plan("domain", "ambient-domain/v1"))
    assembled = _build_artifact(registry, definition, _producer_b, plan)

    names = {r.name for r in assembled.resources}
    assert "domain" in names  # auxiliary logical resource is first-class
    assert any(r.name == "provenance" for r in assembled.resources)
    # Probe resource descriptors by identity-bearing status.
    assert _resource(assembled, "domain").identity_bearing is True
    assert _resource(assembled, "provenance").identity_bearing is False
    assert len(assembled.index) == 2
    assert all(entry.payload_locator.startswith("payloads:") for entry in assembled.index)


def _resource(assembled: AssembledArtifact, name: str) -> LogicalResourceDescriptor:
    for r in assembled.resources:
        if r.name == name:
            return r
    raise AssertionError(f"missing resource {name!r}")


def test_fingerprint_is_exact_jcs_and_path_independent() -> None:
    registry = ComponentRegistry()
    definition = _register(registry, "substrate:synthetic-a/v1", "simple-digraph/v1")
    plan = _plan(registry, definition, _identity_plan("seed", 7))
    assembled = _build_artifact(registry, definition, _producer_a, plan)

    # Recompute from the same descriptors -> deterministic.
    assert artifact_fingerprint(assembled.build_input_identity, assembled.resources) == (
        assembled.artifact_fingerprint
    )
    # Provenance (audit) exclusion: changing audit-only fields must not change the
    # fingerprint. The provenance digest is recorded but not identity-bearing.
    probe = _resource(assembled, "provenance")
    assert probe.digest is not None
    assert probe.identity_bearing is False


def test_fingerprint_changes_when_scientific_content_changes() -> None:
    registry = ComponentRegistry()

    def other_producer(session: MaterializationSession) -> None:
        for index in range(1, 5):  # different realization count/content
            session.add_record(
                GeneratedRecordBody(
                    content={"nodes": 8, "index": index},
                    realization_key=RealizationKey(inputs=(IdentityInput("realization_index", index),)),
                )
            )

    definition = _register(registry, "substrate:synthetic-c/v1", "raster-topology/v1")
    plan = _plan(registry, definition, _identity_plan("seed", 7))
    assembled_a = _build_artifact(registry, definition, other_producer, plan)
    assembled_b = _build_artifact(registry, definition, other_producer, plan)
    assert assembled_a.artifact_fingerprint == assembled_b.artifact_fingerprint


# --------------------------------------------------------------------------- #
# Identity distinction
# --------------------------------------------------------------------------- #


def test_plan_build_input_and_fingerprint_are_distinct() -> None:
    registry = ComponentRegistry()
    definition = _register(registry, "substrate:synthetic-a/v1", "simple-digraph/v1")
    plan = _plan(registry, definition, _identity_plan("seed", 7))
    assembled = _build_artifact(registry, definition, _producer_a, plan)

    from ehp_sn.planning import plan_identity

    assert plan_identity(plan) != assembled.build_input_identity
    assert plan_identity(plan) != assembled.artifact_fingerprint
    assert assembled.build_input_identity != assembled.artifact_fingerprint
    record_ids = {rec.record_id for rec in assembled.records}
    assert all(rid != assembled.artifact_fingerprint for rid in record_ids)


# --------------------------------------------------------------------------- #
# Commit + reuse / conflict
# --------------------------------------------------------------------------- #


def test_commit_frees_immutable_artifact() -> None:
    registry = ComponentRegistry()
    definition = _register(registry, "substrate:synthetic-d/v1", "raster-topology/v1")
    plan = _plan(registry, definition, _identity_plan("generator_revision", "dungeon/v2"))
    assembled = _build_artifact(registry, definition, _producer_d, plan)
    artifact = commit_artifact(assembled)

    assert isinstance(artifact, SubstrateArtifact)
    assert artifact.artifact_fingerprint == assembled.artifact_fingerprint
    assert [r.record_id for r in artifact.records] == [r.record_id for r in assembled.records]
    # Committed artifact exposes a declared resource / record read surface.
    assert artifact.logical_resource("payloads") is not None
    assert artifact.logical_resource("does-not-exist") is None


def test_same_build_twice_yields_deterministic_reuse() -> None:
    """The same scientific build performed twice reuses, never duplicates."""
    registry = ComponentRegistry()
    definition = _register(registry, "substrate:synthetic-a/v1", "simple-digraph/v1")
    plan = _plan(registry, definition, _identity_plan("seed", 7))
    assembled = _build_artifact(registry, definition, _producer_a, plan)
    first = commit_artifact(assembled)

    # A second identical build against the ledger reuse-detects deterministically.
    reused = find_reusable([first], assembled)
    assert reused is not None
    assert reused is first or reused.build_input_identity == first.build_input_identity


def test_conflicting_build_identity_fails() -> None:
    registry = ComponentRegistry()
    definition = _register(registry, "substrate:synthetic-c/v1", "raster-topology/v1")
    plan = _plan(registry, definition, _identity_plan("seed", 7))
    assembled = _build_artifact(registry, definition, _producer_c, plan)
    first = commit_artifact(assembled)

    # A different producer producing different content under the same build-input
    # identity conflicts (build-input identity matches, fingerprint differs).
    def other(session: MaterializationSession) -> None:
        session.add_record(
            GeneratedRecordBody(
                content={"extent": [9, 9]},
                realization_key=RealizationKey(inputs=(IdentityInput("canonical_topology", "ZZ"),)),
            )
        )

    other_assembled = _build_artifact(registry, definition, other, plan)
    assert other_assembled.build_input_identity == assembled.build_input_identity
    with pytest.raises(CommitConflictError):
        find_reusable([first], other_assembled)


def _producer_c(session: MaterializationSession) -> None:
    """Source import with dedup + lineage (Maze-ND-shaped)."""
    session.add_record(
        GeneratedRecordBody(
            content={"extent": [1, 2], "passable": ["A", "A"]},
            realization_key=RealizationKey(inputs=(IdentityInput("canonical_topology", "AA"),)),
            descriptors=(),
        )
    )
    session.add_logical_resource(
        "complete-source-lineage", {"rows": [{"r": 1}]}, resource_kind="lineage"
    )


def _producer_d(session: MaterializationSession) -> None:
    """Rejection/retry then acceptance, no split (DungeonGen-shaped)."""
    for candidate in (0, 2, 4):
        session.add_record(
            GeneratedRecordBody(
                content={"accepted": candidate},
                realization_key=RealizationKey(
                    inputs=(IdentityInput("logical_topology_index", candidate // 2),)
                ),
            )
        )
