"""Producer planning composition for registered substrate definitions.

This module owns the *planning composition*: the explicit association between
authoritative registered definitions and the specific producer-side operations
required to construct a substrate plan.

It is deliberately **not** a framework capability registry, a service locator, a
generic behavior dictionary, or a second discovery authority. The discovery
registry (``ehp_sn.discovery``) remains the single authority for discoverable
definitions; this composition only binds the demonstrated planning operation
(a :data:`~ehp_sn.planning.capability.PlanningResolver`) to a definition object
for the planning orchestration.

Rules that keep this narrow:

* An entry is a :class:`SubstratePlanningRegistration`: a definition object and
  exactly the one typed planning callable it is currently demonstrated to need.
* No ``build`` / ``validate`` / ``inspect`` / ``execute`` / ``artifact`` slots
  are reserved; future lifecycles may use a different composition type.
* Selection is by **definition identity** (``registration.definition is
  definition``), not by canonical reference string, avoiding a second
  canonical-reference authority to keep in sync.

Installed research packages expose their compositions through a framework-owned
entry-point group (:data:`PROVIDER_ENTRY_POINT_GROUP`), mirroring discovery
providers, so ``ehp_sn`` never imports a concrete research package by name
(``ARCH-001``/``ARCH-003``).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from importlib import metadata

from ehp_sn.discovery import DiscoverableDefinition

from .capability import PlanningResolver

#: Entry-point group under which installed packages advertise planning-provider
#: functions. A provider is a zero-argument callable returning an iterable of
#: :class:`SubstratePlanningRegistration` (or a composition).
PROVIDER_ENTRY_POINT_GROUP = "ehp_sn.planning.providers"


@dataclass(frozen=True, slots=True)
class SubstratePlanningRegistration:
    """Bind an authoritative definition to the planning operation it demonstrates.

    ``definition`` is the exact authoritative object the discovery registry holds
    (identity is preserved: ``registry.resolve(def.ref) is registration.definition``).
    ``plan`` is the single typed producer planning callable for that definition:

    .. code-block:: text

        generic loaded configuration
                ↓  plan
        generic PlanningDeclaration
    """

    definition: DiscoverableDefinition
    plan: PlanningResolver


class SubstratePlanningComposition:
    """An immutable, definition-indexed set of substrate planning registrations.

    Constructed once with the explicit registrations; it is not a growable
    registry (no ``add``). Selection is by definition identity, so planning
    resolves the definition from discovery once and then looks up its resolver
    by object identity rather than a second reference key.

    An internal definition->resolver hash index is private implementation state
    of this planning component; it is not a public authority.
    """

    __slots__ = ("_resolvers",)

    def __init__(self, registrations: Iterable[SubstratePlanningRegistration]) -> None:
        self._resolvers: dict[DiscoverableDefinition, PlanningResolver] = {
            registration.definition: registration.plan for registration in registrations
        }

    def __len__(self) -> int:
        return len(self._resolvers)

    def resolver(self, definition: DiscoverableDefinition) -> PlanningResolver | None:
        """Return the planning resolver bound to ``definition``, or ``None``.

        Matches by definition identity (``registration.definition is
        definition``), not by canonical reference.
        """
        return self._resolvers.get(definition)

    def contains(self, definition: DiscoverableDefinition) -> bool:
        """Whether ``definition`` has a registered planning resolver."""
        return definition in self._resolvers


def compose_planning_providers(
    compositions: Iterable[Iterable[SubstratePlanningRegistration]],
) -> SubstratePlanningComposition:
    """Merge explicit registration collections into one composition.

    ``compositions`` is an iterable of registration collections (for example
    each provider's tuple). Entries are merged by definition identity; this is a
    composition-only merge and never touches the discovery registry.
    """
    merged: list[SubstratePlanningRegistration] = []
    for collection in compositions:
        merged.extend(collection)
    return SubstratePlanningComposition(merged)


def effective_planning_composition(
    *,
    group: str = PROVIDER_ENTRY_POINT_GROUP,
) -> SubstratePlanningComposition:
    """Build the effective planning composition from installed providers.

    Each entry point under ``group`` is loaded (importing the owning module) and
    called with no arguments; it returns an iterable of
    :class:`SubstratePlanningRegistration`. The registrations are merged into a
    single immutable composition. ``ehp_sn`` never names a concrete research
    package here.
    """
    collections = [entry_point.load()() for entry_point in metadata.entry_points(group=group)]
    return compose_planning_providers(collections)


__all__ = [
    "PROVIDER_ENTRY_POINT_GROUP",
    "SubstratePlanningComposition",
    "SubstratePlanningRegistration",
    "compose_planning_providers",
    "effective_planning_composition",
]
