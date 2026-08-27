"""Contract tests for the shared ``simple-digraph/v1`` logical record schema.

These tests verify the ``ehp_sn``-owned implementation of
``docs/docs/framework/contracts/relations/simple-digraph-v1.md``: canonical
labelled-graph construction, canonical edge ordering, derived compatibility
properties, and the ``SG-REC-00x`` invariant rejections.

The contract is framework-owned and producer-neutral: the constructor accepts
only contract-owned authoritative inputs (``node_count`` and the unordered
``edges`` set), and it must not know anything about a producing family.
"""

from __future__ import annotations

import pytest
from ehp_sn.contracts.relations import SCHEMA_REF, SimpleDigraphError, simple_digraph


def test_schema_reference() -> None:
    """The contract fixes ``simple-digraph/v1`` as its logical record schema."""
    assert SCHEMA_REF == "simple-digraph/v1"
    assert simple_digraph(3, [(0, 1), (1, 2)]).schema_ref == "simple-digraph/v1"


def test_canonical_edge_ordering_is_lexicographic() -> None:
    """The same unordered edge set canonicalizes to one lexicographic relation."""
    a = simple_digraph(4, [(1, 2), (0, 3), (2, 3), (0, 1)])
    b = simple_digraph(4, [(0, 3), (2, 3), (0, 1), (1, 2)])
    assert a.edges == ((0, 1), (0, 3), (1, 2), (2, 3))
    assert a.edges == b.edges
    assert a == b
    assert a.content() == b.content()


def test_content_equality_is_labelled_not_isomorphic() -> None:
    """Structurally isomorphic graphs with different public labels differ."""
    g = simple_digraph(2, [(0, 1)])
    relabeled = simple_digraph(2, [(1, 0)])
    assert g.content() != relabeled.content()


def test_derived_acyclic_property() -> None:
    """``acyclic`` agrees with the edge relation (SG-REC-006)."""
    assert simple_digraph(3, [(0, 1), (1, 2)]).acyclic is True
    assert simple_digraph(3, [(0, 1), (1, 2), (2, 0)]).acyclic is False


def test_derived_terminal_and_reachability_properties() -> None:
    """``terminal_count`` and ``all_nodes_reach_a_terminal`` agree with content."""
    single = simple_digraph(4, [(0, 2), (1, 2), (2, 3)])
    assert single.terminal_count == 1
    assert single.all_nodes_reach_a_terminal is True

    multi = simple_digraph(4, [(0, 2), (1, 3)])  # terminals 2 and 3
    assert multi.terminal_count == 2
    assert multi.all_nodes_reach_a_terminal is False


def test_contract_does_not_enforce_single_terminal() -> None:
    """A general simple graph need not be single-terminal.

    ``terminal_count == 1`` / ``all_nodes_reach_a_terminal == true`` are a
    producing family's single-terminal guarantee, not requirements of every
    simple directed graph. The constructor must accept a multi-terminal graph.
    """
    multi = simple_digraph(5, [(0, 3), (1, 4), (2, 3)])
    assert multi.terminal_count == 2
    assert not multi.all_nodes_reach_a_terminal


def test_node_count_minimum() -> None:
    """``node_count >= 1`` (SG-REC-001)."""
    with pytest.raises(SimpleDigraphError):
        simple_digraph(0, [])
    with pytest.raises(SimpleDigraphError):
        simple_digraph(-1, [])


def test_invalid_endpoint_rejected() -> None:
    """Endpoints must belong to the dense node domain (SG-REC-002)."""
    with pytest.raises(SimpleDigraphError):
        simple_digraph(3, [(0, 5)])
    with pytest.raises(SimpleDigraphError):
        simple_digraph(3, [(-1, 1)])


def test_self_loop_rejected() -> None:
    """No self-loops (SG-REC-003)."""
    with pytest.raises(SimpleDigraphError):
        simple_digraph(3, [(0, 0)])


def test_duplicate_edge_rejected() -> None:
    """No duplicate edges (SG-REC-003)."""
    with pytest.raises(SimpleDigraphError):
        simple_digraph(3, [(0, 1), (1, 0), (0, 1)])


def test_no_undeclared_attributes() -> None:
    """The scientific payload is exactly ``node_count`` + canonical ``edges``."""
    g = simple_digraph(3, [(0, 1), (1, 2)])
    assert g.content() == {"node_count": 3, "edges": [(0, 1), (1, 2)]}
    assert set(g.content().keys()) == {"node_count", "edges"}


def test_constructed_graph_is_immutable() -> None:
    """Graphs are immutable value objects."""
    from dataclasses import FrozenInstanceError

    g = simple_digraph(3, [(0, 1)])
    with pytest.raises(FrozenInstanceError):
        g.edges = ()  # type: ignore[misc]
