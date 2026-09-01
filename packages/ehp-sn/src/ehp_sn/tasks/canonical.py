"""Generic task catalogue: task definitions, source roles, and composition.

This module owns the framework-level, task-semantic-free shape of a registered
task. A concrete task lives in ``ehp_research``, registers through the
framework-owned task catalogue entry point, and describes:

* its canonical ``task:<name>/v<N>`` reference and scientific purpose;
* the set of **source roles** it requires, each bound to a framework-owned
  logical contract (for example ``raster-topology/v1``) — never to a producer
  identity (Stage 6C § 9);
* the generic runtime capability it exposes for construction/validation
  dispatch.

The framework layer must not invent a universal fixed source tuple such as
``(topology, observations)`` because different tasks require different source
sets (Stage 6C § 9). Source roles are therefore an explicit, per-definition
declaration.

This module imports no concrete research package (ARCH-001) and branches on no
task family (ARCH-003). Scientific meaning is reached only through the methods
of the registered :class:`TaskDefinition` instance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ehp_sn.discovery import DiscoverableDefinition
from ehp_sn.experiments import ComponentRef


@dataclass(frozen=True, slots=True)
class SourceRole:
    """One required source role and the logical contract it must satisfy.

    A role is a **semantic source role**, not a producer identity: the role is
    ``topology`` or ``observation_field`` or ``semantic_graph``, never
    ``dungeongen`` or ``maze-nd``. The corresponding ``required_contract`` is a
    framework-owned logical contract (for example ``raster-topology/v1``). This
    lets a task depend on required capabilities rather than on a concrete
    producer family (Stage 6C § 9).
    """

    role: str
    required_contract: str

    @property
    def canonical(self) -> str:
        """Stable ``role->contract`` canonical form for identity purposes."""
        return f"{self.role}@{self.required_contract}"


@dataclass(frozen=True, slots=True)
class TaskSourceComposition:
    """A task's declared source-role set and its composition policy.

    ``roles`` is the exact set of source roles the task requires; it must not
    be forced into a universal source tuple. ``referenced_contracts`` is the
    distinct set of framework-owned logical contracts the composition consumes.
    ``complete_ambient_compatibility`` records whether the task requires full
    ambient-domain (and where applicable vocabulary) compatibility across its
    spatial sources — relevant to multi-source tasks (Stage 6C § 10).
    """

    roles: tuple[SourceRole, ...]
    complete_ambient_compatibility: bool = True

    @property
    def referenced_contracts(self) -> tuple[str, ...]:
        """Distinct required logical contracts in declaration order."""
        seen: list[str] = []
        for role in self.roles:
            if role.required_contract not in seen:
                seen.append(role.required_contract)
        return tuple(seen)


@runtime_checkable
class TaskDefinition(DiscoverableDefinition, Protocol):
    """A registered, discoverable task definition.

    Extends the framework :class:`DiscoverableDefinition` contract with:

    * ``purpose`` — a short scientific-purpose string for ``tasks list``/``show``;
    * ``sources`` — the task's declared :class:`TaskSourceComposition`;
    * ``build`` — a task-owned corpus builder invoked by generic orchestration;
    * ``validate`` — a task-owned validator invoked by generic orchestration.

    ``build`` and ``validate`` are reached only through this definition instance
    (generic dispatch via the registry); generic orchestration never inspects
    the task's name or source family to decide how to construct or validate it.
    The exact signatures are owned by the generic orchestration contract (see
    ``orchestration.py``) and are implemented by each concrete task.
    """

    @property
    def purpose(self) -> str: ...

    @property
    def sources(self) -> TaskSourceComposition: ...

    def build(self, *, session, sources, configuration, seed) -> object: ...

    def validate(self, *, corpus, sources, configuration) -> object: ...


def task_ref(name: str, version: int = 1) -> ComponentRef:
    """Construct a canonical ``task:<name>/v<N>`` reference."""
    return ComponentRef(kind="task", name=name, version=version)
