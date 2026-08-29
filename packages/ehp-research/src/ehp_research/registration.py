"""Research package integration point for reusable scientific definitions.

This module is the single semantic registration and composition authority for
``ehp_research``. It owns three distinct actions that share bootstrap timing
but remain separate concerns (``docs/invariants.md`` ARCH-001/ARCH-003):

* **component registration** — registering every authoritative reusable
  scientific definition (substrates and figures) into the generic ``ehp_sn``
  component registry, through the single entry point
  (:func:`register_components`);
* **planning composition** — binding each authoritative substrate definition to
  its demonstrated producer planning operation, as planning registrations
  (:func:`planning_registrations`);
* **execution composition** — binding each authoritative substrate definition to
  its demonstrated producer execution operation, as execution registrations
  (:func:`execution_registrations`).

``register_components`` is the one entry point through which reusable
scientific semantic definitions are registered. There is no separate figure
registration path: ``FigureSpec`` definitions enter the same generic component
catalogue as substrate definitions and are owned here. The provider manifest
(``_COMPONENTS``) lists which definitions this package exposes and never
redefines what a definition means; the scientific facts live with each family's
authoritative definition object (its ``ref``, description, and output contract).

Registration is explicit and side-effect free: importing ``ehp_research`` does
not mutate any registry. Population happens only when a consumer calls
:func:`register_components` with an explicit registry instance. Duplicate
handling and duplicate detection are owned by the generic registry itself; this
function deliberately does not re-implement them.
"""

from __future__ import annotations

from collections.abc import Iterable

from ehp_sn.discovery import ComponentRegistry
from ehp_sn.execution import SubstrateExecutionRegistration
from ehp_sn.planning import SubstratePlanningRegistration

from .figures.arena_task_overview import ARENA_TASK_OVERVIEW_SPEC
from .figures.dagflow_overview import DAGFLOW_OVERVIEW_SPEC
from .figures.graph_degree_view import GRAPH_DEGREE_VIEW_SPEC
from .figures.hpc_place_summary import HPC_PLACE_SUMMARY_SPEC
from .figures.hrm_latent_dynamics import HRM_LATENT_DYNAMICS_SPEC
from .substrates import dagflow, dungeongen, maze_nd, obsfield
from .substrates.dagflow import DAGFLOW_DEFINITION
from .substrates.dungeongen import DUNGEONGEN_DEFINITION
from .substrates.maze_nd import MAZE_ND_DEFINITION
from .substrates.obsfield import OBSFIELD_DEFINITION

#: Authoritative reusable scientific definitions admitted to discovery: the
#: Dagflow, Maze-ND, ObsField and DungeonGen substrates plus the reusable
#: scientific figure specs. This is the one registration authority.
_COMPONENTS = (
    DAGFLOW_DEFINITION,
    MAZE_ND_DEFINITION,
    OBSFIELD_DEFINITION,
    DUNGEONGEN_DEFINITION,
    ARENA_TASK_OVERVIEW_SPEC,
    DAGFLOW_OVERVIEW_SPEC,
    GRAPH_DEGREE_VIEW_SPEC,
    HPC_PLACE_SUMMARY_SPEC,
    HRM_LATENT_DYNAMICS_SPEC,
)


def register_components(registry: ComponentRegistry) -> None:
    """Register every reusable scientific definition into ``registry``.

    The operation is explicit: definitions are registered into the caller's
    registry, never into an implicit global. It performs no duplicate detection
    of its own — the generic registry remains the authority, so registering the
    same canonical reference twice raises the generic
    :class:`DuplicateRegistrationError` (``ehp_sn.discovery``).

    This is the single registration path for reusable scientific semantics: it
    installs both substrate definitions and ``FigureSpec`` definitions. It does
    not store producer behavior; planning and execution composition are exposed
    separately via :func:`planning_registrations` and
    :func:`execution_registrations`.
    """
    for definition in _COMPONENTS:
        registry.register(definition)


def planning_registrations() -> tuple[SubstratePlanningRegistration, ...]:
    """Expose the producer planning operations bound to the authoritative definitions.

    Each entry binds the exact authoritative definition object (identity
    preserved with discovery) to its demonstrated :data:`PlanningResolver`
    callable. These registrations are consumed by the framework-owned planning
    composition; they are separate from — and never stored in — the discovery
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
    "register_components",
    "planning_composition_source",
    "execution_composition_source",
    "execution_registrations",
    "planning_registrations",
]
