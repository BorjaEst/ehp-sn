"""Behavioral tests for the release-coordinate ownership boundary (Target 9).

These tests establish that the release number is an *invocation-layer
publication coordinate*, not a scientific configuration field:

* ``--release`` is the highest authority for the intended coordinate; a
  ``release`` value declared in the effective configuration is only a temporary
  compatibility fallback;
* the same scientific config with release 1 vs release 2 selects coordinates
  ``v1`` vs ``v2`` while producing the **same** scientific build identity
  (release never becomes a scientific build-input identity);
* ``plan --release 1`` / ``build --release 1`` resolve the same intended
  coordinate, and build does not re-resolve a different release.

The tests exercise the generic framework planning path with synthetic in-test
producers and resolvers — never a runtime research component — matching the
existing planning test discipline.
"""

from __future__ import annotations

import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from ehp_sn.artifacts import build_input_identity, release_path
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
    ResolvedResource,
    ResourceRequirement,
    SubstratePlanningComposition,
    SubstratePlanningRegistration,
    plan_substrate,
)


@dataclass(frozen=True)
class _Definition:
    """Minimal in-test discoverable substrate definition."""

    ref: ComponentRef
    kind: str
    description: str
    output_contract: str


def _loaded(values: Mapping[str, Any]) -> LoadedConfiguration:
    return LoadedConfiguration(source=Path("synthetic.toml"), values=values)


def _variant_plan(variant: str, seed: int) -> PlanningResolver:
    """A planning resolver declaring a canonical ``variant`` identity input.

    ``variant`` is required for the framework to resolve a release coordinate
    from (family, variant, release).
    """

    def plan(document: LoadedConfiguration) -> PlanningDeclaration:
        return PlanningDeclaration(
            configuration={"seed": seed},
            resources=(),
            identity_inputs=(
                IdentityInput("variant", variant),
                IdentityInput("seed", seed),
            ),
        )

    return plan


class _Resolver:
    """The minimal generic binder for an empty resource set."""

    def resolve(self, requirement: ResourceRequirement) -> ResolvedResource:
        raise AssertionError("no resources are declared in these plans")


def _plan_for(
    *,
    release: int | None,
    config_values: dict[str, Any],
    variant: str = "source-topology",
    seed: int = 7,
):
    """Plan ``substrate:maze-synthetic/v1`` for the given release and config."""
    definition = _Definition(
        ref=ComponentRef.parse("substrate:maze-synthetic/v1"),
        kind="substrate",
        description="synthetic release-ownership substrate",
        output_contract="raster-topology/v1",
    )
    registry = ComponentRegistry()
    registry.register(definition)
    composition = SubstratePlanningComposition(
        (SubstratePlanningRegistration(definition=definition, plan=_variant_plan(variant, seed)),)
    )
    document = _loaded(config_values)
    return plan_substrate(
        registry,
        composition,
        "substrate:maze-synthetic/v1",
        document,
        resource_resolver=_Resolver(),
        release=release,
    )


def test_invocation_release_selects_the_coordinate() -> None:
    """``--release 1``/``2`` (no config release) resolve ``v1``/``v2``."""
    plan_v1 = _plan_for(release=1, config_values={})
    plan_v2 = _plan_for(release=2, config_values={})

    assert plan_v1.release_coordinate is not None
    assert plan_v2.release_coordinate is not None
    assert plan_v1.release_coordinate.version == "v1"
    assert plan_v2.release_coordinate.version == "v2"
    assert plan_v1.release_coordinate.name == "maze-synthetic/source-topology"
    assert plan_v2.release_coordinate.name == "maze-synthetic/source-topology"


def test_config_release_is_only_a_fallback() -> None:
    """Without ``--release``, a config-level release is used (temporary fallback)."""
    plan = _plan_for(release=None, config_values={"release": 3})

    assert plan.release_coordinate is not None
    assert plan.release_coordinate.version == "v3"


def test_invocation_release_overrides_config_release() -> None:
    """``--release`` is the highest authority over a config-level release."""
    plan = _plan_for(release=5, config_values={"release": 3})

    assert plan.release_coordinate is not None
    assert plan.release_coordinate.release == 5


def test_missing_release_leaves_coordinate_unresolved() -> None:
    """No ``--release`` and no config release → coordinate stays unresolved."""
    plan = _plan_for(release=None, config_values={})

    assert plan.release_coordinate is None


def test_different_release_same_scientific_build_identity() -> None:
    """Release 1 vs release 2 → same coordinate-selection-independent identity.

    Release is a publication coordinate, never a scientific build-input
    identity: the two plans describe the same build semantics at different
    publication coordinates.
    """
    plan_v1 = _plan_for(release=1, config_values={})
    plan_v2 = _plan_for(release=2, config_values={})

    assert build_input_identity(plan_v1) == build_input_identity(plan_v2)


def test_different_seed_different_scientific_build_identity() -> None:
    """A scientific identity input change still changes build identity."""
    plan_a = _plan_for(release=1, config_values={}, seed=7)
    plan_b = _plan_for(release=1, config_values={}, seed=8)

    assert build_input_identity(plan_a) != build_input_identity(plan_b)


def test_positive_release_required() -> None:
    """A non-positive release is rejected by coordinate resolution."""
    from ehp_sn.planning import ReleaseCoordinateResolutionError

    for bad in (0, -1):
        with pytest.raises(ReleaseCoordinateResolutionError):
            _plan_for(release=bad, config_values={})


def test_plan_and_build_use_the_same_intended_coordinate(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``plan --release 1`` and ``build --release 1`` resolve the same coordinate.

    Build must not re-resolve a different release than the caller selected.
    This is enforced by ``build_substrate`` passing its ``release`` argument
    through to ``plan_substrate`` exactly once (Target 9).
    """
    from ehp_sn.artifacts import build_substrate
    from ehp_sn.planning import ReleaseCoordinate

    definition = _Definition(
        ref=ComponentRef.parse("substrate:maze-synthetic/v1"),
        kind="substrate",
        description="synthetic release-ownership substrate",
        output_contract="raster-topology/v1",
    )
    registry = ComponentRegistry()
    registry.register(definition)
    planning = SubstratePlanningComposition(
        (SubstratePlanningRegistration(definition=definition, plan=_variant_plan("source-topology", 7)),)
    )

    def _execute(session: MaterializationSession) -> None:
        session.add_record(
            GeneratedRecordBody(
                content={"value": 1},
                realization_key=RealizationKey(inputs=(IdentityInput("realization_index", 1),)),
            )
        )

    execution = SubstrateExecutionComposition(
        (SubstrateExecutionRegistration(definition=definition, execute=_execute),)
    )

    # The plan selected with --release 1 targets v1.
    planned = plan_substrate(
        registry,
        planning,
        "substrate:maze-synthetic/v1",
        _loaded({}),
        resource_resolver=_Resolver(),
        release=1,
    )
    assert planned.release_coordinate is not None
    assert planned.release_coordinate.version == "v1"

    # Building with the same config and --release 1 commits exactly v1 — not a
    # different, reinferred coordinate.
    with tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False) as f:
        f.write("[generation]\nseed = 7\n")  # scientific config, no release field
        config_path = f.name

    outcome = build_substrate(
        registry=registry,
        planning_composition=planning,
        execution_composition=execution,
        target="substrate:maze-synthetic/v1",
        config=config_path,
        resource_resolver=_Resolver(),
        root=tmp_path,
        release=1,
    )
    assert outcome.action == "committed"
    final = release_path(
        tmp_path,
        ReleaseCoordinate(family="maze-synthetic", variant="source-topology", release=1),
    )
    assert final.is_dir()
    # The same scientific config must not have been re-resolved to another release.
    assert not release_path(
        tmp_path,
        ReleaseCoordinate(family="maze-synthetic", variant="source-topology", release=2),
    ).exists()
