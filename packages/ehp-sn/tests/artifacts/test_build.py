"""Behavioral tests for the generic ``build_substrate`` orchestration (Phase 4C).

These tests verify that the single generic build operation composes the
established planning / execution / artifact stages exactly once and returns a
framework-domain :class:`BuildOutcome`:

* ``build_substrate`` is the single configuration-to-plan path; *only* it may
  call ``load_configuration`` / ``plan_substrate`` — execution and commit never
  re-plan or re-resolve (verified by counting calls);
* the exact plan produced by planning is the one executed and assembled;
* the build outcome distinguishes the real lifecycle outcomes ``committed`` and
  ``reused``, carries no exit code and no physical location, and exposes the
  committed :class:`SubstrateArtifact`;
* producer-specific exceptions are translated to a controlled
  :class:`BuildError`, not leaked through the public lifecycle;
* a failed build never yields an artifact discovery would treat as valid.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from ehp_sn.artifacts import (
    BuildError,
    SubstrateArtifact,
    build_substrate,
    release_path,
)
from ehp_sn.configuration import LoadedConfiguration
from ehp_sn.discovery import ComponentRegistry
from ehp_sn.execution import (
    GeneratedRecordBody,
    MaterializationSession,
    RealizationKey,
    SubstrateExecutionComposition,
    SubstrateExecutionRegistration,
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
)


@dataclass(frozen=True)
class SyntheticDefinition:
    ref: ComponentRef
    kind: str
    description: str
    output_contract: str


class _ResourceResolver:
    def resolve(self, requirement: ResourceRequirement) -> ResolvedResource:
        if requirement.definition_resource_ref is None:
            from ehp_sn.planning import ResourceResolutionError

            raise ResourceResolutionError(f"no declared reference for {requirement.ref!r}")
        return ResolvedResource(
            requirement_ref=requirement.ref,
            resource_ref=requirement.definition_resource_ref,
            resolution_source="definition",
        )


class _Producer:
    def __init__(self, name: str) -> None:
        self.name = name
        self.invocations = 0

    def __call__(self, session: MaterializationSession) -> None:
        self.invocations += 1
        session.add_record(
            GeneratedRecordBody(
                content={"name": self.name},
                realization_key=RealizationKey(inputs=(IdentityInput("realization_index", 1),)),
            )
        )


def _loaded(values: Mapping[str, Any]) -> LoadedConfiguration:
    return LoadedConfiguration(source=Path("synthetic.toml"), values=values)


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


def _write_config(seed: int = 7) -> str:
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False) as f:
        # release is a framework-owned root-level artifact-coordinate field.
        f.write("release = 1\n[generation]\nseed = 7\n")
        return f.name


def _compositions(
    registry: ComponentRegistry,
    ref: str = "substrate:synthetic-a/v1",
    plan_value: Any = 7,
    producer: Callable[[MaterializationSession], None] | None = None,
):
    component_ref = ComponentRef.parse(ref)
    definition = SyntheticDefinition(
        ref=component_ref,
        kind="substrate",
        description=f"synthetic {component_ref.name}",
        output_contract="simple-digraph/v1",
    )
    registry.register(definition)
    planning = SubstratePlanningComposition(
        (SubstratePlanningRegistration(definition=definition, plan=_plan_resolver("seed", plan_value)),)
    )
    producer = producer or _Producer("a")
    execution = SubstrateExecutionComposition(
        (SubstrateExecutionRegistration(definition=definition, execute=producer),)
    )
    return definition, planning, execution, producer


def test_build_plans_and_resolves_exactly_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """load_configuration and plan_substrate are called exactly once (by build).

    Execution and commit never re-plan or re-resolve; a second resolution would
    make the counts exceed one and fail the test.
    """
    import tempfile

    calls = {"load": 0, "plan": 0}
    import ehp_sn.artifacts.build as build_mod

    real_load = build_mod.load_configuration
    real_plan = build_mod.plan_substrate

    def counting_load(path: str):
        calls["load"] += 1
        return real_load(path)

    def counting_plan(
        registry, planning_composition, target, document, *, resource_resolver, release=None
    ):
        calls["plan"] += 1
        return real_plan(
            registry,
            planning_composition,
            target,
            document,
            resource_resolver=resource_resolver,
            release=release,
        )

    monkeypatch.setattr(build_mod, "load_configuration", counting_load)
    monkeypatch.setattr(build_mod, "plan_substrate", counting_plan)

    config_path = _write_config()
    root = Path(tempfile.mkdtemp())

    registry = ComponentRegistry()
    _, planning, execution, _ = _compositions(registry)
    outcome = build_substrate(
        registry=registry,
        planning_composition=planning,
        execution_composition=execution,
        target="substrate:synthetic-a/v1",
        config=config_path,
        resource_resolver=_ResourceResolver(),
        root=root,
    )

    assert calls["load"] == 1
    assert calls["plan"] == 1
    assert outcome.action == "committed"
    assert isinstance(outcome.artifact, SubstrateArtifact)


def test_build_committed_outcome_shape() -> None:
    import tempfile

    config_path = _write_config()
    root = Path(tempfile.mkdtemp())

    registry = ComponentRegistry()
    _, planning, execution, _ = _compositions(registry)
    outcome = build_substrate(
        registry=registry,
        planning_composition=planning,
        execution_composition=execution,
        target="substrate:synthetic-a/v1",
        config=config_path,
        resource_resolver=_ResourceResolver(),
        root=root,
    )

    assert outcome.action == "committed"
    # A durable committed release exists (Targets 4/8).
    final = release_path(
        root, ReleaseCoordinate(family="synthetic-a", variant="single-terminal", release=1)
    )
    assert final.is_dir()


def test_build_second_identical_build_reuses_without_producer(tmp_path) -> None:
    """Same build twice: second resolves reusable and does NOT re-invoke producer."""
    config_path = _write_config()
    producer = _Producer("a")

    registry = ComponentRegistry()
    _, planning, execution, _ = _compositions(registry, producer=producer)
    first = build_substrate(
        registry=registry,
        planning_composition=planning,
        execution_composition=execution,
        target="substrate:synthetic-a/v1",
        config=config_path,
        resource_resolver=_ResourceResolver(),
        root=tmp_path,
    )
    assert first.action == "committed"
    assert producer.invocations == 1

    second = build_substrate(
        registry=registry,
        planning_composition=planning,
        execution_composition=execution,
        target="substrate:synthetic-a/v1",
        config=config_path,
        resource_resolver=_ResourceResolver(),
        root=tmp_path,
    )
    assert second.action == "reused"
    # Reuse resolves the existing committed release without producer execution.
    assert producer.invocations == 1
    assert second.artifact.artifact_fingerprint == first.artifact.artifact_fingerprint
    assert second.artifact.location == first.artifact.location


def test_build_needs_configured_release(tmp_path) -> None:
    """A build without a release coordinate fails (framework never auto-assigns).

    ``--release N`` is the canonical source; the error message points at it
    rather than at a config-declared value.
    """
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False) as f:
        f.write("[generation]\nseed = 7\n")
        config_path = f.name

    from ehp_sn.artifacts import ReleaseNotConfiguredBuildError

    registry = ComponentRegistry()
    _, planning, execution, _ = _compositions(registry)
    with pytest.raises(ReleaseNotConfiguredBuildError) as excinfo:
        build_substrate(
            registry=registry,
            planning_composition=planning,
            execution_composition=execution,
            target="substrate:synthetic-a/v1",
            config=config_path,
            resource_resolver=_ResourceResolver(),
            root=tmp_path,
        )
    assert "requires --release" in str(excinfo.value)


def test_producer_exception_is_translated_to_build_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import tempfile

    config_path = _write_config()
    root = Path(tempfile.mkdtemp())

    def exploding_producer(session: MaterializationSession) -> None:
        raise ValueError("producer internal failure")

    registry = ComponentRegistry()
    _, planning, execution, _ = _compositions(registry, producer=exploding_producer)

    with pytest.raises(BuildError):
        build_substrate(
            registry=registry,
            planning_composition=planning,
            execution_composition=execution,
            target="substrate:synthetic-a/v1",
            config=config_path,
            resource_resolver=_ResourceResolver(),
            root=root,
        )


def test_build_outcome_has_no_cli_categories() -> None:
    """The framework outcome carries no exit code and no physical location."""
    import dataclasses

    from ehp_sn.artifacts.outcome import BuildOutcome as BO

    field_names = {field_.name for field_ in dataclasses.fields(BO)}
    assert {"action", "artifact"} == field_names
    assert "exit_code" not in field_names
    assert "location" not in field_names
    assert "status" not in field_names
