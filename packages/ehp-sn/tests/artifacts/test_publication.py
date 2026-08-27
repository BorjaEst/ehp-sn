"""Lifecycle tests for the corrected durable substrate publication (Phase 4B-D).

These tests assert the architectural invariants of the durable publication
boundary, not only happy-path filesystem creation:

* an assembled artifact alone is not committed and not durable (no release);
* a successful publication leaves a real, resolvable committed release — even in
  a fresh resolver context (fresh process equivalence);
* a failed publication leaves no partial release at the final coordinate;
* the producer never learns the final physical path;
* auxiliary logical resources and record payloads persist generically with no
  family branches;
* the artifact fingerprint is coherent before and after serialization.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from ehp_sn.artifacts import (
    AssembledArtifact,
    artifact_ref,
    assemble_artifact,
    inspect_release,
    publish_artifact,
    release_path,
    resolve_release,
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
    ResolvedResource,
    ResourceRequirement,
    SubstratePlanningComposition,
    SubstratePlanningRegistration,
    plan_substrate,
)


@dataclass(frozen=True)
class Def:
    ref: ComponentRef
    kind: str
    description: str
    output_contract: str


class _Resolver:
    def resolve(self, requirement: ResourceRequirement) -> ResolvedResource:
        if requirement.definition_resource_ref is None:
            from ehp_sn.planning import ResourceResolutionError

            raise ResourceResolutionError(f"no declared reference for {requirement.ref!r}")
        return ResolvedResource(
            requirement_ref=requirement.ref,
            resource_ref=requirement.definition_resource_ref,
            resolution_source="definition",
        )


def _producer_with_aux(session: MaterializationSession, *, aux: bool = True) -> None:
    session.add_record(
        GeneratedRecordBody(
            content={"nodes": 4},
            realization_key=RealizationKey(inputs=(IdentityInput("realization_index", 1),)),
        )
    )
    if aux:
        session.add_logical_resource(
            "complete-source-lineage", {"rows": [{"r": 1}, {"r": 2}]}, resource_kind="lineage"
        )


def _plan_resolver(name: str, value: Any) -> PlanningResolver:
    def plan(document: LoadedConfiguration) -> PlanningDeclaration:
        return PlanningDeclaration(
            configuration={"value": value},
            resources=(),
            identity_inputs=(
                IdentityInput(name, value),
                IdentityInput("variant", "single-terminal"),
            ),
        )

    return plan


def _build_assembled(
    producer, *, release: int = 2, variant: str = "single-terminal"
) -> tuple[AssembledArtifact, ReleaseCoordinate]:
    registry = ComponentRegistry()
    ref = ComponentRef.parse("substrate:familyx/v1")
    definition = Def(ref=ref, kind="substrate", description="x", output_contract="schema/v1")
    registry.register(definition)
    planning = SubstratePlanningComposition(
        (SubstratePlanningRegistration(definition=definition, plan=_plan_resolver("seed", 7)),)
    )
    execution = SubstrateExecutionComposition(
        (SubstrateExecutionRegistration(definition=definition, execute=producer),)
    )
    document = LoadedConfiguration(
        source=Path("x.toml"), values={"substrate": {"variant": variant}, "release": release}
    )
    plan = plan_substrate(registry, planning, ref, document, resource_resolver=_Resolver())
    result = execute_substrate(registry, execution, plan)
    assembled = assemble_artifact(plan, result)
    return assembled, ReleaseCoordinate(family="familyx", variant=variant, release=release)


def test_assembled_alone_not_durable_not_committed(tmp_path) -> None:
    """An assembled artifact alone leaves no committed release."""
    assembled, coordinate = _build_assembled(_producer_with_aux)
    assert inspect_release(tmp_path, coordinate).committed_exists is False
    assert not release_path(tmp_path, coordinate).exists()
    # It is a candidate, not a committed artifact with a coordinate/reference.
    assert not hasattr(assembled, "release_coordinate")


def test_successful_commit_release_exists_and_resolves_fresh(tmp_path) -> None:
    """A committed release exists and resolves in a fresh resolver context."""
    assembled, coordinate = _build_assembled(_producer_with_aux)
    artifact = publish_artifact(assembled, root=tmp_path, coordinate=coordinate)

    final = release_path(tmp_path, coordinate)
    assert final.is_dir()
    # Fresh resolver context (equivalent to a new process) resolves the same
    # durable artifact with the same identity/fingerprint and logical records.
    resolved = resolve_release(tmp_path, coordinate)
    assert resolved.build_input_identity == artifact.build_input_identity
    assert resolved.artifact_fingerprint == artifact.artifact_fingerprint
    assert [r.record_id for r in resolved.records] == [r.record_id for r in artifact.records]


def test_failed_publication_leaves_no_partial_final_release(tmp_path, monkeypatch) -> None:
    """A publish failure leaves no valid final release and no staged path appears committed."""
    assembled, coordinate = _build_assembled(_producer_with_aux)
    final = release_path(tmp_path, coordinate)

    # Force the atomic rename to fail after staging is fully written + verified.
    import os

    def _boom(src, dst, *, src_dir_fd=None, dst_dir_fd=None):
        raise OSError("simulated atomic publication failure")

    monkeypatch.setattr(os, "rename", _boom)
    from ehp_sn.artifacts import StoreError

    with pytest.raises(StoreError):
        publish_artifact(assembled, root=tmp_path, coordinate=coordinate)

    # No committed release appears at the final coordinate.
    assert not final.exists()
    assert inspect_release(tmp_path, coordinate).committed_exists is False


def test_fingerprint_coherent_before_and_after_serialization(tmp_path) -> None:
    """The artifact fingerprint is identical before and after durable serialization."""
    assembled, coordinate = _build_assembled(_producer_with_aux)
    published = publish_artifact(assembled, root=tmp_path, coordinate=coordinate)
    # The committed fingerprint equals the assembled candidate's fingerprint.
    assert published.artifact_fingerprint == assembled.artifact_fingerprint
    # And the committed manifest's fingerprint is internally consistent.
    import json

    manifest = json.loads((release_path(tmp_path, coordinate) / "manifest.json").read_text())
    assert manifest["artifact_fingerprint"] == assembled.artifact_fingerprint


def test_auxiliary_resources_persisted_generically(tmp_path) -> None:
    """Adding an auxiliary logical resource persists it without publisher code changes."""
    assembled, coordinate = _build_assembled(_producer_with_aux)
    publish_artifact(assembled, root=tmp_path, coordinate=coordinate)
    resolved = resolve_release(tmp_path, coordinate)
    aux_names = {r.name for r in resolved.auxiliary}
    assert "complete-source-lineage" in aux_names
    lineage = next(r for r in resolved.auxiliary if r.name == "complete-source-lineage")
    assert lineage.content == {"rows": [{"r": 1}, {"r": 2}]}
    # It is a declared logical resource on the committed artifact.
    assert resolved.logical_resource("complete-source-lineage") is not None


def test_record_payloads_persisted_generically(tmp_path) -> None:
    """Record payloads are persisted as logical records and resolve identically."""
    assembled, coordinate = _build_assembled(_producer_with_aux)
    publish_artifact(assembled, root=tmp_path, coordinate=coordinate)
    resolved = resolve_release(tmp_path, coordinate)
    assert len(resolved.records) == 1
    assert resolved.records[0].content == {"nodes": 4}
    # The committed record index exposes each record.
    assert len(resolved.index) == 1
    assert resolved.record(resolved.records[0].record_id) is not None


def test_artifact_reference_follows_release_coordinate(tmp_path) -> None:
    """The artifact reference follows the release-coordinate reference grammar."""
    assembled, coordinate = _build_assembled(_producer_with_aux, release=5)
    assert artifact_ref(coordinate) == "artifact:familyx/single-terminal/v5"
    artifact = publish_artifact(assembled, root=tmp_path, coordinate=coordinate)
    assert artifact.artifact_ref == "artifact:familyx/single-terminal/v5"


def test_reuse_returns_the_existing_committed_release(tmp_path) -> None:
    """The same candidate published twice reuses the existing committed release."""
    assembled, coordinate = _build_assembled(_producer_with_aux)
    first = publish_artifact(assembled, root=tmp_path, coordinate=coordinate)
    second = publish_artifact(assembled, root=tmp_path, coordinate=coordinate)
    assert second.location == first.location
    assert second.build_input_identity == first.build_input_identity


def test_forcing_release_change_moves_the_coordinate(tmp_path) -> None:
    """A different configured release is a different immutable coordinate (no overwrite)."""
    assembled, coordinate_v1 = _build_assembled(_producer_with_aux, release=1)
    publish_artifact(assembled, root=tmp_path, coordinate=coordinate_v1)
    # Same candidate at a different release: a distinct coordinate, not an overwrite.
    assembled2, coordinate_v2 = _build_assembled(_producer_with_aux, release=2)
    publish_artifact(assembled2, root=tmp_path, coordinate=coordinate_v2)
    assert release_path(tmp_path, coordinate_v1).is_dir()
    assert release_path(tmp_path, coordinate_v2).is_dir()
