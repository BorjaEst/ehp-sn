"""Authoritative generic ``build_substrate`` orchestration (Target 6 / Phase 4C).

This module owns the single generic orchestration operation for a substrate
build, connecting the three already-established generic stages:

```text
build(target, config, ...)
    ↓
P = plan_substrate(...)          exactly once (only config-to-plan path)
    ↓
R = validate/readiness(P)        execute_substrate establishes readiness
    ↓
M = execute(P, R)                execute_substrate (producer execution)
    ↓
A = assemble(P, M)               artifact assembly (framework metadata)
    ↓
reuse/commit(A)                  find_reusable / commit_artifact
    ↓
BuildOutcome
```

It composes—never reimplements—the framework stages. ``plan_substrate`` remains
the only configuration-to-plan path; build does not independently resolve
configuration or bind resources. ``execute_substrate`` receives the exact
``ExecutionPlan``; artifact assembly receives the materialization produced from
that same plan.

Producer-specific exceptions are translated at this framework boundary into a
controlled :class:`BuildError` (with the original preserved as cause) so no
producer-specific exception escapes directly through the generic public
lifecycle; they are not converted here into CLI exit codes (the CLI does that at
its own layer).
"""

from __future__ import annotations

from collections.abc import Iterable

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
    ResourceResolver,
    SubstratePlanningComposition,
    plan_substrate,
)

from .artifact import SubstrateArtifact
from .assembly import assemble_artifact
from .commit import CommitConflictError, commit_artifact, find_reusable
from .outcome import BuildOutcome


class BuildError(Exception):
    """A controlled framework build failure at the generic public boundary.

    Raised when a substrate build cannot complete. It is a framework-domain
    error, not a CLI category; the CLI maps it at its own layer. The originating
    producer exception (if any) is preserved as the cause for diagnostics.
    """


def build_substrate(
    *,
    registry: ComponentRegistry,
    planning_composition: SubstratePlanningComposition,
    execution_composition: SubstrateExecutionComposition,
    target: str,
    config: str,
    resource_resolver: ResourceResolver,
    existing: Iterable[SubstrateArtifact] = (),
) -> BuildOutcome:
    """Run one full generic substrate build from a configuration path.

    Loads the configuration through the generic loader and plans exactly once
    via ``plan_substrate`` (the only configuration-to-plan path), then executes
    the exact plan, assembles the framework artifact metadata, and commits or
    reuses deterministically. No family conditional, raster path, source path,
    or split assumption appears here.

    ``existing`` supplies already-committed artifacts (if any) so the build can
    decide deterministic reuse versus conflict versus fresh commit; the framework
    never maintains a store itself.

    Raises :class:`BuildError` for a producer-specific (or otherwise unknown)
    execution/assembly failure translated at this boundary. Framework-controlled
    errors (configuration access/parse, planning, execution validation, or a
    commit conflict) propagate unchanged so the CLI can map them to their own
    categories; they are not collapsed into a single build error.
    """
    document = load_configuration(config)
    plan = plan_substrate(
        registry,
        planning_composition,
        target,
        document,
        resource_resolver=resource_resolver,
    )
    try:
        result = execute_substrate(registry, execution_composition, plan)
        assembled = assemble_artifact(plan, result)
        reusable = find_reusable(existing, assembled)
    except (
        ExecutionError,
        ConfigurationAccessError,
        ConfigurationParseError,
        PlanningError,
        CommitConflictError,
    ):
        # Framework-controlled failures propagate so the caller can map them.
        raise
    except Exception as exc:  # noqa: BLE001
        # Producer-specific (or otherwise unknown) failure: translate at the
        # framework boundary into a BuildError, preserving the cause.
        raise BuildError("substrate build failed") from exc

    if reusable is not None:
        return BuildOutcome(action="reused", artifact=reusable)
    committed = commit_artifact(assembled)
    return BuildOutcome(action="committed", artifact=committed)


__all__ = ["BuildError", "build_substrate"]
