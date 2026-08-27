"""Shared raster topology contract (``raster-topology/v1``).

This module is the ``ehp_sn``-owned implementation of the framework contract
specified by ``docs/docs/framework/contracts/topology/raster-topology-v1.md``.

It defines a producer-agnostic, consumer-agnostic logical record schema for a
raster movement structure: which positions in an ambient spatial domain are
traversable, and how movement between them is defined.

The constructor accepts only the two authoritative inputs — a canonical
``rectangular-row-column/v1`` ambient domain and a ``passable`` structure over
it — and owns every fixed ``raster-topology/v1`` derivation under the fixed
schema parameters:

.. code-block:: text

    topology_kind:    raster
    coordinate_system: row-column
    movement_kind:    grid4
    directed:         false
    edge_cost_kind:   unit
    stay_included:    false

Authoritative representation: ``passable[position]``.
Canonical derived views: ``state_count``, ``state_to_position``,
``position_to_state``, ``next_state``, ``movement_valid``, ``component_count``,
``connected``.

It is framework-owned and producer-neutral: it knows nothing about a producing
family, source lineage, generator profile, connectivity acceptance policy,
largest-component selection, or retry.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final

from ..domains import RectangularRowColumnDomain

#: The canonical logical record schema reference.
SCHEMA_REF: Final = "raster-topology/v1"

#: Fixed ``v1`` schema parameters (same for every conforming record).
TOPOLOGY_KIND: Final = "raster"
COORDINATE_SYSTEM: Final = "row-column"
MOVEMENT_KIND: Final = "grid4"
DIRECTED: Final = False
EDGE_COST_KIND: Final = "unit"
STAY_INCLUDED: Final = False

#: Cardinal movement labels under ``grid4`` (deterministic canonical order).
#: The transition relation is derived from row/column adjacency of passable
#: positions.
MOVEMENT_LABELS: Final = ("north", "east", "south", "west")

#: Row/column deltas for each movement label (north, east, south, west).
_MOVEMENT_DELTAS: Final = (
    (-1, 0),
    (0, 1),
    (1, 0),
    (0, -1),
)


class RasterTopologyError(ValueError):
    """A supplied topology does not conform to ``raster-topology/v1``.

    Raised for a mismatched passability length, an all-blocked domain, or an
    invalid binding. It is a contract-domain error; producers translate it.
    """


@dataclass(frozen=True, slots=True)
class RasterTopology:
    """An immutable, conforming ``raster-topology/v1`` record.

    ``domain`` is the complete ``rectangular-row-column/v1`` ambient-domain
    declaration and ``passable`` is the authoritative passability structure in
    canonical row-major order. Every other field is a canonical derived view
    reconstrucible from these two, under the fixed ``v1`` schema parameters.
    """

    # Authoritative
    domain: RectangularRowColumnDomain
    passable: tuple[bool, ...]

    # Canonical derived views
    state_count: int
    state_to_position: tuple[int, ...]
    position_to_state: tuple[int | None, ...]
    next_state: tuple[dict[str, int], ...]
    movement_valid: tuple[dict[str, bool], ...]
    component_count: int
    connected: bool

    @property
    def schema_ref(self) -> str:
        """The canonical logical record schema reference."""
        return SCHEMA_REF

    @property
    def topology_kind(self) -> str:
        """Fixed schema parameter: ``raster``."""
        return TOPOLOGY_KIND

    @property
    def movement_kind(self) -> str:
        """Fixed schema parameter: ``grid4``."""
        return MOVEMENT_KIND

    @property
    def directed(self) -> bool:
        """Fixed schema parameter: ``False``."""
        return DIRECTED

    @property
    def edge_cost_kind(self) -> str:
        """Fixed schema parameter: ``unit``."""
        return EDGE_COST_KIND

    @property
    def stay_included(self) -> bool:
        """Fixed schema parameter: ``False`` (no topology self-loops)."""
        return STAY_INCLUDED

    def content(self) -> dict[str, object]:
        """Return the authoritative content projection (domain + passable).

        Record identity and equality are based on ``extent`` (domain) and
        ``passable``; the canonical derived views carry no identity beyond them.
        """
        return {
            "domain": self.domain.declaration(),
            "passable": list(self.passable),
        }


def _derive_views(
    domain: RectangularRowColumnDomain,
    passable: tuple[bool, ...],
) -> tuple[
    int,
    tuple[int, ...],
    tuple[int | None, ...],
    tuple[dict[str, int], ...],
    tuple[dict[str, bool], ...],
    int,
    bool,
]:
    """Compute all canonical derived views from domain + passable (RT-REC-003..007)."""
    position_count = domain.position_count
    height, width = domain.height, domain.width

    # RT-REC-003 — compact state enumeration in canonical row-major passable order.
    state_to_position: list[int] = [p for p in range(position_count) if passable[p]]
    state_count = len(state_to_position)
    position_to_state: list[int | None] = [None] * position_count
    for state_id, position in enumerate(state_to_position):
        position_to_state[position] = state_id

    # RT-REC-004/006 — grid4, undirected, no stay. next_state/movement_valid keyed
    # by (state_id, movement label).
    next_state: list[dict[str, int]] = [dict() for _ in range(state_count)]
    movement_valid: list[dict[str, bool]] = [dict() for _ in range(state_count)]
    for state_id, position in enumerate(state_to_position):
        row, col = domain.coordinate(position)
        for label, (drow, dcol) in zip(MOVEMENT_LABELS, _MOVEMENT_DELTAS, strict=True):
            nrow, ncol = row + drow, col + dcol
            if 0 <= nrow < height and 0 <= ncol < width:
                neighbor = domain.position_id(nrow, ncol)
                if passable[neighbor]:
                    neighbor_state = position_to_state[neighbor]
                    assert neighbor_state is not None  # passable -> has a state
                    next_state[state_id][label] = neighbor_state
                    movement_valid[state_id][label] = True
                else:
                    movement_valid[state_id][label] = False
            else:
                movement_valid[state_id][label] = False

    # RT-REC-007 — connected components under grid4 adjacency over passable.
    # RT-REC-005 — the relation is symmetric (undirected), so components are
    # computed over the undirected adjacency.
    component_labels = [-1] * state_count
    component_count = 0
    for start in range(state_count):
        if component_labels[start] != -1:
            continue
        component_labels[start] = component_count
        stack = [start]
        while stack:
            state_id = stack.pop()
            for _label, target in next_state[state_id].items():
                if component_labels[target] == -1:
                    component_labels[target] = component_count
                    stack.append(target)
        component_count += 1

    connected = component_count == 1
    return (
        state_count,
        tuple(state_to_position),
        tuple(position_to_state),
        tuple(next_state),
        tuple(movement_valid),
        component_count,
        connected,
    )


def raster_topology(domain: RectangularRowColumnDomain, passable: Sequence[bool]) -> RasterTopology:
    """Construct a conforming :class:`RasterTopology` from authoritative inputs.

    Accepts a canonical rectangular ``domain`` and a ``passable`` structure of
    exactly ``domain.position_count`` booleans in canonical row-major order
    (``RT-REC-002``). Computes all fixed ``raster-topology/v1`` derived views
    under the fixed grid4/undirected/unit/no-stay parameters.

    Raises :class:`RasterTopologyError` for a passability length mismatch or a
    fully non-passable domain (``state_count`` must be ``>= 1``).
    """
    if len(passable) != domain.position_count:
        raise RasterTopologyError(
            f"passable length {len(passable)} != position_count {domain.position_count}"
        )
    bools = tuple(bool(p) for p in passable)
    if not any(bools):
        raise RasterTopologyError("at least one position must be passable (RT-REC-002)")

    (
        state_count,
        state_to_position,
        position_to_state,
        next_state,
        movement_valid,
        component_count,
        connected,
    ) = _derive_views(domain, bools)

    return RasterTopology(
        domain=domain,
        passable=bools,
        state_count=state_count,
        state_to_position=state_to_position,
        position_to_state=position_to_state,
        next_state=next_state,
        movement_valid=movement_valid,
        component_count=component_count,
        connected=connected,
    )


__all__ = [
    "COORDINATE_SYSTEM",
    "DIRECTED",
    "EDGE_COST_KIND",
    "MOVEMENT_KIND",
    "MOVEMENT_LABELS",
    "RasterTopology",
    "RasterTopologyError",
    "SCHEMA_REF",
    "STAY_INCLUDED",
    "TOPOLOGY_KIND",
    "raster_topology",
]
