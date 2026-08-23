"""Research package integration point for definitions and planning composition.

This module is the *package integration point* for ``ehp_research``. It owns two
distinct actions that share bootstrap timing but remain separate concerns
(``docs/invariants.md`` ARCH-001/ARCH-003):

* **discovery installation** — registering authoritative research definition
  objects into the generic ``ehp_sn`` discovery registry
  (:func:`register_components`);
* **planning composition** — exposing the demonstrated producer planning
  operation bound to each authoritative definition, as planning registrations
  (:func:`planning_registrations`).

The provider manifest (``_COMPONENTS``) lists which definitions this package
exposes. It never redefines what a definition means and never duplicates a
definition's metadata; the scientific facts live with each family's
authoritative definition object (its ``ref``, description, and output contract)
and each family's planning resolver.

Registration is explicit and side-effect free: importing ``ehp_research`` does
not mutate any registry. Population happens only when a consumer calls
:func:`register_components` with an explicit registry instance. Duplicate
handling and duplicate detection are owned by the generic registry itself;
this function deliberately does not re-implement them.

The planning composition is built from :func:`planning_registrations` by an
application bootstrap; it is independent of the discovery registry and is never
stored there.

See ``docs/invariants.md`` ARCH-001/ARCH-003 and the package README's
"Registration and discovery" section.
"""

from __future__ import annotations

from collections.abc import Iterable

from ehp_sn.discovery import ComponentRegistry
from ehp_sn.planning import SubstratePlanningRegistration

from .substrates import dagflow, maze_nd
from .substrates.dagflow import DAGFLOW_DEFINITION
from .substrates.maze_nd import MAZE_ND_DEFINITION

#: Authoritative Dagflow and Maze-ND definitions admitted to discovery.
#: DungeonGen and ObsField are intentionally not registered yet (phase control:
#: they serve as later generality tests).
_COMPONENTS = (
    DAGFLOW_DEFINITION,
    MAZE_ND_DEFINITION,
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
    )


def planning_composition_source() -> Iterable[SubstratePlanningRegistration]:
    """Entry-point provider: the planning registrations for this package.

    Advertised under the framework-owned ``ehp_sn.planning.providers`` group so
    an application bootstrap can compose installed research planning without
    ``ehp_sn`` importing this package by name.
    """
    return planning_registrations()


__all__ = [
    "planning_composition_source",
    "planning_registrations",
    "register_components",
]
