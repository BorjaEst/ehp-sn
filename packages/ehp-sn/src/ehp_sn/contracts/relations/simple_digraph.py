"""Shared simple directed graph contract (``simple-digraph/v1``).

This module is the ``ehp_sn``-owned implementation of the framework contract
specified by ``docs/docs/framework/contracts/relations/simple-digraph-v1.md``.

It defines a producer-agnostic, consumer-agnostic logical record schema for a
**simple directed graph**: a dense public node domain and a directed edge
relation over it. Concrete substrate families (for example a procedurally
generated graph family) produce records that conform to this contract; concrete
task families consume them. Neither side is named here.

The contract owns exactly the semantics of a general simple directed graph:

* a dense public node domain ``{0, ..., node_count - 1}`` (``SG-REC-001``);
* a directed edge relation over that domain with no endpoint outside it
  (``SG-REC-002``);
* a simple relation: no duplicate edge and no self-loop (``SG-REC-003``);
* canonical lexicographic ``(source, target)`` edge ordering (``SG-REC-004``);
* no undeclared graph/node/edge attributes (``SG-REC-005``);
* derived compatibility properties that agree exactly with the relation
  (``SG-REC-006``): ``acyclic``, ``terminal_count``, and
  ``all_nodes_reach_a_terminal``.

It deliberately does **not** enforce any producer-specific structural class such
as "exactly one terminal reached by every node" — that is a producing family's
guarantee (its `single-terminal` capability), enforced by the producer's own
validation, not by the general simple directed graph contract.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final

#: The canonical logical record schema reference.
SCHEMA_REF: Final = "simple-digraph/v1"


class SimpleDigraphError(ValueError):
    """A supplied graph does not conform to ``simple-digraph/v1``.

    Raised by :func:`simple_digraph` (or a strict validator) when the node
    count or edge relation violates a contract invariant. It is a
    contract-domain error; producers translate it at their own layer.
    """


def _validate(node_count: int, edges: Sequence[tuple[int, int]]) -> None:
    """Raise :class:`SimpleDigraphError` for any ``SG-REC-00x`` violation."""
    # SG-REC-001 — node domain
    if not isinstance(node_count, int) or isinstance(node_count, bool):
        raise SimpleDigraphError("node_count must be an integer")
    if node_count < 1:
        raise SimpleDigraphError(f"node_count must be >= 1, got {node_count}")

    seen: set[tuple[int, int]] = set()
    for source, target in edges:
        # SG-REC-002 — edge domain
        if not isinstance(source, int) or isinstance(source, bool):
            raise SimpleDigraphError(f"edge source {source!r} is not an integer")
        if not isinstance(target, int) or isinstance(target, bool):
            raise SimpleDigraphError(f"edge target {target!r} is not an integer")
        if not (0 <= source < node_count):
            raise SimpleDigraphError(
                f"edge source {source} outside public node domain [0, {node_count})"
            )
        if not (0 <= target < node_count):
            raise SimpleDigraphError(
                f"edge target {target} outside public node domain [0, {node_count})"
            )
        # SG-REC-003 — simple directed relation (no self-loop, no duplicate)
        if source == target:
            raise SimpleDigraphError(f"self-loop edge ({source}, {source}) is not permitted")
        if (source, target) in seen:
            raise SimpleDigraphError(f"duplicate edge ({source}, {target}) is not permitted")
        seen.add((source, target))


def _canonicalize(edges: Sequence[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    """Return edges sorted lexicographically by ``(source, target)``.

    This is the canonical serialized ordering required by ``SG-REC-004``.
    Insertion / generation order is non-semantic.
    """
    return tuple(sorted(edges))


def _is_acyclic(node_count: int, edges: tuple[tuple[int, int], ...]) -> bool:
    """Return ``True`` when the edge relation contains no directed cycle.

    Uses Kahn's algorithm over the adjacency relation; the input is guaranteed
    simple (no self-loops, no duplicates) by construction.
    """
    out_edges: list[list[int]] = [[] for _ in range(node_count)]
    in_degree = [0] * node_count
    for source, target in edges:
        out_edges[source].append(target)
        in_degree[target] += 1

    stack = [node for node in range(node_count) if in_degree[node] == 0]
    visited = 0
    while stack:
        node = stack.pop()
        visited += 1
        for nxt in out_edges[node]:
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                stack.append(nxt)
    return visited == node_count


def _all_nodes_reach(terminal: int, node_count: int, edges: tuple[tuple[int, int], ...]) -> bool:
    """Return ``True`` when every node has a directed path to ``terminal``.

    Follows edges from every node through its descendants (edges are directed
    forward); a node reaches ``terminal`` if ``terminal`` is in its reachable
    closure. Every node trivially reaches itself via the zero-length path.
    """
    adjacency: list[list[int]] = [[] for _ in range(node_count)]
    for source, target in edges:
        adjacency[source].append(target)

    for start in range(node_count):
        if start == terminal:
            continue
        seen = {start}
        stack = [start]
        reached = False
        while stack:
            node = stack.pop()
            for nxt in adjacency[node]:
                if nxt == terminal:
                    reached = True
                    break
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
            if reached:
                break
        if not reached:
            return False
    return True


@dataclass(frozen=True, slots=True)
class SimpleDigraph:
    """An immutable, conforming ``simple-digraph/v1`` record.

    ``node_count`` is the cardinality of the dense public node domain
    ``{0, ..., node_count - 1}``. ``edges`` is the canonical simple directed
    edge relation, ordered lexicographically by ``(source, target)``
    (``SG-REC-004``). The derived properties ``acyclic``, ``terminal_count``
    and ``all_nodes_reach_a_terminal`` are canonical derived compatibility
    views of the authoritative content (``node_count`` + ``edges``) and agree
    with it exactly (``SG-REC-006``).

    Content equality is labelled-graph equality: two records are
    content-identical exactly when they have the same ``node_count`` and the
    same canonical directed edge relation. Structural isomorphism with a
    different public labelling is *not* content equality.
    """

    node_count: int
    edges: tuple[tuple[int, int], ...]

    #: Whether the edge relation contains a directed cycle (derived).
    acyclic: bool
    #: Number of nodes with out-degree zero (derived).
    terminal_count: int
    #: Whether every node reaches at least one terminal (derived).
    all_nodes_reach_a_terminal: bool

    @property
    def schema_ref(self) -> str:
        """The canonical logical record schema reference."""
        return SCHEMA_REF

    def content(self) -> dict[str, object]:
        """Return the canonical labelled content projection.

        This is the authoritative scientific content used for labelled-graph
        equality: ``node_count`` and the canonical edge relation.
        """
        return {"node_count": self.node_count, "edges": list(self.edges)}


def simple_digraph(
    node_count: int,
    edges: Sequence[tuple[int, int]],
) -> SimpleDigraph:
    """Construct a conforming :class:`SimpleDigraph` from authoritative inputs.

    Accepts only contract-owned authoritative inputs: ``node_count`` and the
    unordered ``edges`` set. It validates every ``SG-REC-00x`` invariant,
    canonicalizes the edge relation lexicographically, and computes the derived
    compatibility properties.

    Raises :class:`SimpleDigraphError` for an invalid node count, an endpoint
    outside the node domain, a self-loop, or a duplicate edge.
    """
    raw = list(edges)
    _validate(node_count, raw)
    canonical = _canonicalize(raw)

    out_degree = [0] * node_count
    for source, _target in canonical:
        out_degree[source] += 1
    terminal_count = sum(1 for degree in out_degree if degree == 0)
    acyclic = _is_acyclic(node_count, canonical)

    all_reach = False
    if terminal_count == 1:
        terminal = next(node for node, degree in enumerate(out_degree) if degree == 0)
        all_reach = _all_nodes_reach(terminal, node_count, canonical)

    return SimpleDigraph(
        node_count=node_count,
        edges=canonical,
        acyclic=acyclic,
        terminal_count=terminal_count,
        all_nodes_reach_a_terminal=all_reach,
    )


__all__ = [
    "SCHEMA_REF",
    "SimpleDigraph",
    "SimpleDigraphError",
    "simple_digraph",
]
