"""Research package integration point for definitions and planning composition.

This module is the *package integration point* for ``ehp_research``. It owns
three distinct actions that share bootstrap timing but remain separate concerns
(``docs/invariants.md`` ARCH-001/ARCH-003):

* **discovery installation** — registering authoritative research definition
  objects into the generic ``ehp_sn`` discovery registry
  (:func:`register_components`);
* **planning composition** — exposing the demonstrated producer planning
  operation bound to each authoritative definition, as planning registrations
  (:func:`planning_registrations`);
* **execution composition** — exposing the demonstrated producer execution
  operation bound to each authoritative definition, as execution registrations
  (:func:`execution_registrations`).

The provider manifest (``_COMPONENTS``) lists which definitions this package
exposes. It never redefines what a definition means and never duplicates a
definition's metadata; the scientific facts live with each family's
authoritative definition object (its ``ref``, description, and output contract)
and each family's planning/execution resolvers.

Registration is explicit and side-effect free: importing ``ehp_research`` does
not mutate any registry. Population happens only when a consumer calls
:func:`register_components` with an explicit registry instance. Duplicate
handling and duplicate detection are owned by the generic registry itself;
this function deliberately does not re-implement them.

The planning composition is built from :func:`planning_registrations`, and the
execution composition from :func:`execution_registrations`, by an application
bootstrap; both are independent of the discovery registry and are never stored
there.

See ``docs/invariants.md`` ARCH-001/ARCH-003 and the package README's
"Registration and discovery" section.
"""

from __future__ import annotations

from collections.abc import Iterable

from ehp_sn.discovery import ComponentRegistry
from ehp_sn.execution import SubstrateExecutionRegistration
from ehp_sn.planning import SubstratePlanningRegistration

from .substrates import dagflow, dungeongen, maze_nd, obsfield
from .substrates.dagflow import DAGFLOW_DEFINITION
from .substrates.dungeongen import DUNGEONGEN_DEFINITION
from .substrates.maze_nd import MAZE_ND_DEFINITION
from .substrates.obsfield import OBSFIELD_DEFINITION

#: Authoritative Dagflow, Maze-ND, ObsField, and DungeonGen definitions
#: admitted to discovery.
_COMPONENTS = (
    DAGFLOW_DEFINITION,
    MAZE_ND_DEFINITION,
    OBSFIELD_DEFINITION,
    DUNGEONGEN_DEFINITION,
)


def register_components(registry: ComponentRegistry) -> None:
    """Register the research definitions exposed by this package into ``registry``.

    The operation is explicit: definitions are registered into the caller's
    registry, never into an implicit global. It performs no duplicate detection
    of its own — the generic registry remains the authority, so registering the
    same canonical reference twice raises the generic
    :class:`DuplicateRegistrationError` (``ehp_sn.discovery``).

    This function installs *only definitions* into discovery. It does not store
    producer behavior; planning composition is exposed separately via
    :func:`planning_registrations`.
    """
    for definition in _COMPONENTS:
        registry.register(definition)


def planning_registrations() -> tuple[SubstratePlanningRegistration, ...]:
    """Expose the producer planning operations bound to the authoritative definitions.

    Each entry binds the exact authoritative definition object (identity
    preserved with discovery) to its demonstrated :data:`PlanningResolver`
    callable. These registrations are consumed by the framework-owned planning
    composition ; they are separate from — and never stored in — the discovery
    registry.
    """
    return (
        SubstratePlanningRegistration(definition=DAGFLOW_DEFINITION, plan=dagflow.plan),
        SubstratePlanningRegistration(definition=MAZE_ND_DEFINITION, plan=maze_nd.plan),
        SubstratePlanningRegistration(definition=OBSFIELD_DEFINITION, plan=obsfield.plan),
        SubstratePlanningRegistration(definition=DUNGEONGEN_DEFINITION, plan=dungeongen.plan),
    )


def planning_composition_source() -> Iterable[SubstratePlanningRegistration]:
    """Entry-point provider: the planning registrations for this package.

    Advertised under the framework-owned ``ehp_sn.planning.providers`` group so
    an application bootstrap can compose installed research planning without
    ``ehp_sn`` importing this package by name.
    """
    return planning_registrations()


def execution_registrations() -> tuple[SubstrateExecutionRegistration, ...]:
    """Expose the producer execution operations bound to authoritative definitions.

    Each entry binds the exact authoritative definition object (identity
    preserved with discovery) to its demonstrated :data:`ExecutionOperation`
    callable. These registrations are consumed by the framework-owned execution
    composition; they are separate from — and never stored in — the discovery
    registry.

    Only definitions whose execution is genuinely conforming for
    specification-ready configurations are registered here. A definition that
    remains blocked by unresolved scientific decisions is intentionally absent
    so the generic lifecycle reports a clean
    :class:`~ehp_sn.execution.MissingExecutionCapabilityError` rather than an
    operation that raises ``NotImplementedError``.

    Maze-ND is registered because its execution operation is conforming for the
    specified ``source-topology`` variant: it loads and verifies the exact bound
    immutable source, extracts/normalizes/deduplicates unique normalized
    topologies through the shared ``raster-topology/v1`` constructor, preserves
    complete source lineage, and materializes records plus the lineage resource
    through the framework ``MaterializationSession``.

    DungeonGen is registered because its execution operation is conforming for
    the specified ``general`` variant: it verifies the frozen external
    dependency is build-ready and, per logical topology index, deterministically
    derives the candidate seed, invokes the exact upstream layout generator,
    converts to passability, applies the largest-component policy, normalizes
    the extent, evaluates the acceptance policy under a retry budget, and
    materializes each accepted normalized topology through the shared
    ``raster-topology/v1`` constructor plus a complete production-lineage
    resource via the framework ``MaterializationSession``.
    """
    return (
        SubstrateExecutionRegistration(definition=DAGFLOW_DEFINITION, execute=dagflow.execute),
        SubstrateExecutionRegistration(definition=MAZE_ND_DEFINITION, execute=maze_nd.execute),
        SubstrateExecutionRegistration(definition=OBSFIELD_DEFINITION, execute=obsfield.execute),
        SubstrateExecutionRegistration(definition=DUNGEONGEN_DEFINITION, execute=dungeongen.execute),
    )


def execution_composition_source() -> Iterable[SubstrateExecutionRegistration]:
    """Entry-point provider: the execution registrations for this package.

    Advertised under the framework-owned ``ehp_sn.execution.providers`` group so
    an application bootstrap can compose installed research execution without
    ``ehp_sn`` importing this package by name.
    """
    return execution_registrations()


__all__ = [
    "execution_composition_source",
    "execution_registrations",
    "planning_composition_source",
    "planning_registrations",
    "register_components",
]
