"""Producer execution composition for registered substrate definitions.

This module owns the *execution composition*: the explicit association between
authoritative registered definitions and the specific producer-side execution
operation required to run one substrate build. It is the execution counterpart of
``ehp_sn.planning.composition`` and follows the identical discipline.

It is deliberately **not** a capability registry, a service locator, a generic
behavior dictionary, or a second discovery authority. The discovery registry
(``ehp_sn.discovery``) remains the single authority for discoverable
definitions. This composition only binds the demonstrated execution operation
(a :data:`~ehp_sn.execution.operation.ExecutionOperation`) to a definition
object for the execution orchestration.

Rules that keep this narrow:

* An entry is a :class:`SubstrateExecutionRegistration`: a definition object and
  exactly the one typed execution callable it is currently demonstrated to need.
  No ``resolve`` / ``plan`` / ``validate`` / ``inspect`` / ``artifact`` slots are
  reserved; planning and execution are separate, independently composed
  lifecycles.
* Selection is by **definition identity** (``registration.definition is
  definition``), not by canonical reference string, avoiding a second
  canonical-reference authority to keep in sync — the same choice planning makes.

Installed research packages expose their execution compositions through a
framework-owned entry-point group (:data:`PROVIDER_ENTRY_POINT_GROUP`), so
``ehp_sn`` never imports a concrete research package by name
(``ARCH-001``/``ARCH-003``). Capability 9 defines the composition and its
entry-point surface; concrete research execution operations are plugged in by
later capabilities.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from importlib import metadata

from ehp_sn.discovery import DiscoverableDefinition

from .operation import ExecutionOperation

#: Entry-point group under which installed packages advertise execution-provider
#: functions. A provider is a zero-argument callable returning an iterable of
#: :class:`SubstrateExecutionRegistration`.
PROVIDER_ENTRY_POINT_GROUP = "ehp_sn.execution.providers"


@dataclass(frozen=True, slots=True)
class SubstrateExecutionRegistration:
    """Bind an authoritative definition to the execution operation it demonstrates.

    ``definition`` is the exact authoritative object the discovery registry holds
    (identity is preserved: ``registry.resolve(def.ref) is registration.definition``).
    ``execute`` is the single typed producer execution callable for that
    definition:

    .. code-block:: text

        framework materialization session
                ↓  execute
        populated session (records + auxiliary resources)
    """

    definition: DiscoverableDefinition
    execute: ExecutionOperation


class SubstrateExecutionComposition:
    """An immutable, definition-indexed set of substrate execution registrations.

    Constructed once with the explicit registrations; it is not a growable
    registry (no ``add``). Selection is by definition identity, so execution
    resolves the definition from discovery once and then looks up its operation
    by object identity rather than a second reference key.

    An internal definition->operation hash index is private implementation state
    of this execution component; it is not a public authority.
    """

    __slots__ = ("_operations",)

    def __init__(self, registrations: Iterable[SubstrateExecutionRegistration]) -> None:
        self._operations: dict[DiscoverableDefinition, ExecutionOperation] = {
            registration.definition: registration.execute for registration in registrations
        }

    def __len__(self) -> int:
        return len(self._operations)

    def execute(self, definition: DiscoverableDefinition) -> ExecutionOperation | None:
        """Return the execution operation bound to ``definition``, or ``None``.

        Matches by definition identity (``registration.definition is
        definition``), not by canonical reference.
        """
        return self._operations.get(definition)

    def contains(self, definition: DiscoverableDefinition) -> bool:
        """Whether ``definition`` has a registered execution operation."""
        return definition in self._operations


def compose_execution_providers(
    compositions: Iterable[Iterable[SubstrateExecutionRegistration]],
) -> SubstrateExecutionComposition:
    """Merge explicit registration collections into one composition.

    ``compositions`` is an iterable of registration collections (for example
    each provider's tuple). Entries are merged by definition identity; this is a
    composition-only merge and never touches the discovery registry.
    """
    merged: list[SubstrateExecutionRegistration] = []
    for collection in compositions:
        merged.extend(collection)
    return SubstrateExecutionComposition(merged)


def effective_execution_composition(
    *,
    group: str = PROVIDER_ENTRY_POINT_GROUP,
) -> SubstrateExecutionComposition:
    """Build the effective execution composition from installed providers.

    Each entry point under ``group`` is loaded (importing the owning module) and
    called with no arguments; it returns an iterable of
    :class:`SubstrateExecutionRegistration`. The registrations are merged into a
    single immutable composition. ``ehp_sn`` never names a concrete research
    package here.
    """
    collections = [entry_point.load()() for entry_point in metadata.entry_points(group=group)]
    return compose_execution_providers(collections)


__all__ = [
    "PROVIDER_ENTRY_POINT_GROUP",
    "SubstrateExecutionComposition",
    "SubstrateExecutionRegistration",
    "compose_execution_providers",
    "effective_execution_composition",
]
