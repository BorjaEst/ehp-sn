from __future__ import annotations

from dataclasses import dataclass

from . import _core

SCHEMA_REF = "simple-digraph"
V1 = f"{SCHEMA_REF}/v1"


@dataclass(frozen=True)
class SimpleDigraph(_core.Relation):
    """A `simple-digraph/v1` logical record.

    The authoritative content is the public node domain (`node_count`) and the
    simple directed-edge relation (`edges`). `edges` is modelled as a set
    because `simple-digraph/v1` treats edge order as non-semantic: labelled-graph
    identity is determined by the edge set, not by construction or insertion
    order. Derived compatibility properties such as acyclicity or terminal
    reachability, and the record invariants, belong to later slices rather than
    to this structural shell.
    """

    record_id: str
    node_count: int
    edges: frozenset[tuple[int, int]]


@dataclass(frozen=True)
class Artifact: ...


__all__ = ["Artifact", "SCHEMA_REF", "V1", "SimpleDigraph"]
