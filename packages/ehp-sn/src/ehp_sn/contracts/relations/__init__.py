"""Relational graph contracts (``ehp_sn`` framework-owned).

Subpackage re-exports the relational graph contract implementations, for
example :data:`~ehp_sn.contracts.relations.simple_digraph.SimpleDigraph`.
The normative semantics live in ``docs/docs/framework/contracts/relations/``.
"""

from __future__ import annotations

from .simple_digraph import (
    SCHEMA_REF,
    SimpleDigraph,
    SimpleDigraphError,
    simple_digraph,
)

__all__ = [
    "SCHEMA_REF",
    "SimpleDigraph",
    "SimpleDigraphError",
    "simple_digraph",
]
