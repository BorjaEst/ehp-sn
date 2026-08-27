"""Authoritative generic ``build_substrate`` orchestration (Phase 4C / 4B-D).

This module owns the single generic orchestration operation for a substrate
build, connecting the established generic stages in the corrected durable
lifecycle:

```text
build(target, config, root)
    ↓
P = plan_substrate(...)          exactly once (only config-to-plan path)
    ↓
coordinate = P.release_coordinate (configured release, never auto-assigned)
    ↓
state = inspect_release + classify_planning_state
    │   reusable ────────────────→ resolve existing → BuildOutcome(reused)
    │   conflict ────────────────→ controlled failure
    │   invalid_existing_state ──→ controlled failure
    ↓   available
M = execute(P, R)                execute_substrate (producer execution)
    ↓
A = assemble(P, M)               artifact assembly (framework metadata)
    ↓
C = publish_artifact(A)          durable staging + verify + atomic publish
    ↓
BuildOutcome(committed, C)
```

It composes—never reimplements—the framework stages, and closes an
:class:`AssembledArtifact` only through durable publication. Reuse resolves an
existing committed release **without** invoking the producer (Target 9);
conflict and invalid-existing-state are controlled failures (Target 2).
``plan_substrate`` remains the only configuration-to-plan path; build does not
independently resolve configuration or bind resources.

Producer-specific exceptions are translated at this framework boundary into a
controlled :class:`BuildError` (with the original preserved as cause) so no
producer-specific exception escapes directly through the generic public
lifecycle; they are not converted here into CLI exit codes (the CLI does that
at its own layer).
"""

from __future__ import annotations

from pathlib import Path

from ehp_sn.configuration import (
    ConfigurationAccessError,
    ConfigurationParseError,
    load_configuration,
)
from ehp_sn.discovery import ComponentRegistry
from ehp_sn.execution import (
    ExecutionError,
    SubstrateExecutionComposition,
    execute_substrate,
)
from ehp_sn.planning import (
    PlanningError,
    PlanningState,
    ReleaseCoordinate,
    ResourceResolver,
    SubstratePlanningComposition,
    classify_planning_state,
    plan_substrate,
)

from .assembly import assemble_artifact
from .build_errors import (
    BuildError,
    ConflictBuildError,
    InvalidExistingStateBuildError,
    ReleaseNotConfiguredBuildError,
)
from .commit import (
    InvalidExistingStateError,
    ReleaseNotConfiguredError,
    publish_artifact,
)
from .identity import build_input_identity
from .outcome import BuildOutcome
from .resolve import resolve_release
from .store import ExistingState, StoreError, inspect_release


def build_substrate(
    *,
    registry: ComponentRegistry,
    planning_composition: SubstratePlanningComposition,
    execution_composition: SubstrateExecutionComposition,
    target: str,
    config: str,
    resource_resolver: ResourceResolver,
    root: Path,
    release: int | None = None,
) -> BuildOutcome:
    """Run one full generic substrate build from a configuration path.

    Loads the configuration through the generic loader, plans exactly once via
    ``plan_substrate`` (the only configuration-to-plan path), resolves the
    intended release coordinate, classifies the physical destination state
    (available / reusable / conflict / invalid existing state), and then either
    reuses an existing committed release (without producer execution) or
    executes the exact plan, assembles, and durably publishes the artifact.

    ``release`` is the invocation-layer release selection (the ``--release`` CLI
    parameter). It selects *where* this concrete publication is committed and is
    the highest authority for the intended coordinate; a ``release`` value
    declared in the effective configuration is a temporary compatibility
    fallback. Release is a publication coordinate, never a scientific
    build-input identity — a build must not re-resolve a different release than
    the one the caller selected.

    ``root`` is the artifact root under which committed releases are placed
    (``data/interim/<family>/<variant>/v<N>/`` for the monorepo backend).

    Raises:

    * :class:`ReleaseNotConfiguredBuildError` when the effective configuration
      declares no release coordinate (the framework never auto-assigns one);
    * :class:`ConflictBuildError` when an immutable release coordinate is
      occupied by different content;
    * :class:`InvalidExistingStateBuildError` when the destination contains
      incomplete/corrupt content;
    * :class:`BuildError` for a producer-specific (or otherwise unknown)
      execution/assembly/publication failure translated at this boundary.

    Framework-controlled errors (configuration access/parse, planning,
    execution validation, store conflicts) propagate so the CLI can map them to
    their own categories.
    """
    document = load_configuration(config)
    plan = plan_substrate(
        registry,
        planning_composition,
        target,
        document,
        resource_resolver=resource_resolver,
        release=release,
    )
    coordinate = _require_coordinate(plan.release_coordinate)

    state = _classify_destination(root, coordinate, plan)
    if state is PlanningState.REUSABLE:
        artifact = resolve_release(root, coordinate)
        return BuildOutcome(action="reused", artifact=artifact)
    if state is PlanningState.CONFLICT:
        raise ConflictBuildError(
            f"release coordinate {coordinate.name!r} v{coordinate.release} already "
            "commits a different build-input identity; choose a new configured release"
        )
    if state is PlanningState.INVALID_EXISTING_STATE:
        raise InvalidExistingStateBuildError(
            f"release coordinate {coordinate.name!r} v{coordinate.release} contains "
            "incomplete or corrupt content and cannot be treated as committed"
        )

    try:
        result = execute_substrate(registry, execution_composition, plan)
        assembled = assemble_artifact(plan, result)
        artifact = publish_artifact(assembled, root=root, coordinate=coordinate)
    except (
        ExecutionError,
        ConfigurationAccessError,
        ConfigurationParseError,
        PlanningError,
        StoreError,
        InvalidExistingStateError,
        ReleaseNotConfiguredError,
    ):
        # Framework-controlled failures propagate so the caller can map them.
        raise
    except Exception as exc:  # noqa: BLE001
        # Producer-specific (or otherwise unknown) failure: translate at the
        # framework boundary into a BuildError, preserving the cause.
        raise BuildError("substrate build failed") from exc

    return BuildOutcome(action="committed", artifact=artifact)


def _require_coordinate(coordinate: ReleaseCoordinate | None) -> ReleaseCoordinate:
    """Return the resolved release coordinate, requiring it to be present.

    The release number is an invocation-layer publication coordinate supplied
    via ``--release N`` (the canonical source). A ``release`` value declared in
    the effective configuration is only a legacy compatibility fallback. When
    neither is present the coordinate is unresolved and the build cannot
    publish; the framework never auto-assigns a release number.
    """
    if coordinate is None:
        raise ReleaseNotConfiguredBuildError(
            "data build requires --release N; the framework does not auto-assign release numbers"
        )
    return coordinate


def _classify_destination(
    root: Path,
    coordinate: ReleaseCoordinate,
    plan,
) -> PlanningState:
    """Classify the physical destination state for the planned build."""
    existing: ExistingState = inspect_release(root, coordinate)
    planned_identity = build_input_identity(plan)
    return classify_planning_state(
        committed_exists=existing.committed_exists,
        existing_build_input_identity=existing.build_input_identity,
        valid_existing=existing.valid,
        planned_build_input_identity=planned_identity,
    )


__all__ = ["BuildError", "build_substrate"]
