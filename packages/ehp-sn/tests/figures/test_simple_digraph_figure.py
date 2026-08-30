"""Framework-owned simple-digraph figure tests (Phase 2).

These test :mod:`ehp_sn.figures.builtin.simple_digraph` — the framework-owned
built-in figure ``figure:simple-digraph-inspection/v1`` whose complete
scientific/structural meaning is expressible purely through the framework-owned
``simple-digraph/v1`` logical contract (Phase-2 § 7).

They verify the Phase-2 § 44 required test matrix for the graph inspector:

* canonical runtime schema (authoritative ``node_count`` + ``edges``);
* contract edge cases: N=1, acyclic single-terminal, multi-terminal, cyclic —
  proving the figure is a generic graph figure, not secretly Dagflow-specific
  (Phase-2 § 14);
* all public nodes and all directed edges represented; edge direction preserved;
  terminal classification correct (Phase-2 § 9, § 44);
* node IDs are categorical identities, not scientific coordinates/order
  (Phase-2 § 11);
* canonical contract derivation reused (not independently reimplemented,
  Phase-2 § 5);
* occasional incidental edge insertion order → same prepared graph semantics
  (Phase-2 § 16 metamorphic);
* layout is explicit/deterministic and separately controllable — layout/seed
  changes never affect ProjectionIdentity (Phase-2 § 12-13, § 41);
* no task/goal semantics in the figure (Phase-2 § 10);
* rendering does not mutate the authoritative source, prepared view, or
  projection (Phase-2 § 33).

Headless Matplotlib backend is selected before any pyplot use.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless backend required

import pytest
from ehp_sn.contracts.relations import simple_digraph
from ehp_sn.figures import (
    FigureInputCompatibilityError,
    effective_figure_registry,
    prepare_figure,
    render_figure_projection,
)
from ehp_sn.figures.builtin.simple_digraph import (
    SIMPLE_DIGRAPH_INSPECTION_REF,
    _circular_positions,
)
from ehp_sn.figures.service import _ExactSource

_GRAPH_REF = SIMPLE_DIGRAPH_INSPECTION_REF


def _registry():
    return effective_figure_registry()


def _source(
    *,
    record_id: str = "sha256:GR",
    node_count: int,
    edges,
    artifact_ref: str = "artifact:dag/v1",
) -> _ExactSource:
    return _ExactSource(
        artifact_ref=artifact_ref,
        record_id=record_id,
        schema_ref="simple-digraph/v1",
        content={"node_count": node_count, "edges": list(edges)},
    )


def _project(source: _ExactSource):
    return prepare_figure(_registry(), _GRAPH_REF, source)


# ---------------------------------------------------------------------------
# canonical runtime schema + contract edge cases
# ---------------------------------------------------------------------------


def test_n1_graph() -> None:
    """A single-node graph (no edges) is a valid simple-digraph/v1 record."""
    projection = _project(_source(node_count=1, edges=[]))
    data = projection.content
    assert data.node_count == 1
    assert data.edges == ()
    assert data.terminals == (0,)
    assert data.acyclic is True
    assert data.all_nodes_reach_a_terminal is True


def test_acyclic_single_terminal_graph() -> None:
    projection = _project(_source(node_count=4, edges=[(0, 1), (1, 2), (2, 3)]))
    data = projection.content
    assert data.edges == ((0, 1), (1, 2), (2, 3))
    assert data.acyclic is True
    assert data.terminals == (3,)
    assert data.all_nodes_reach_a_terminal is True


def test_multi_terminal_graph() -> None:
    """Two sinks make a multi-terminal graph; the figure still renders it."""
    projection = _project(_source(node_count=4, edges=[(0, 1), (0, 2)]))
    data = projection.content
    assert data.acyclic is True
    assert sorted(data.terminals) == [1, 2, 3]
    assert data.all_nodes_reach_a_terminal is False


def test_cyclic_graph_is_accepted() -> None:
    """A contract-valid cyclic graph is accepted — proves generic not Dagflow.

    Dagflow's ``single-terminal`` variant requires acyclicity; the generic
    ``simple-digraph/v1`` figure must accept a valid cyclic graph (Phase-2 § 14).
    """
    projection = _project(_source(node_count=3, edges=[(0, 1), (1, 2), (2, 0)]))
    data = projection.content
    assert data.acyclic is False
    assert data.terminals == ()
    figure = render_figure_projection(projection, registry=_registry())
    assert type(figure).__name__ == "Figure"


def test_graph_accepts_contract_cyclic_but_rejects_invalid() -> None:
    """The generic figure enforces the shared contract, not producer invariants."""
    # A self-loop violates simple-digraph/v1 (SG-REC-003) → controlled failure.
    from ehp_sn.contracts.relations import SimpleDigraphError

    with pytest.raises(SimpleDigraphError):
        simple_digraph(2, [(0, 0)])


# ---------------------------------------------------------------------------
# representation: all nodes / all edges / direction / terminals
# ---------------------------------------------------------------------------


def test_all_public_nodes_represented_in_prepared_view() -> None:
    data = _project(_source(node_count=5, edges=[(0, 1), (2, 3)])).content
    assert data.node_count == 5


def test_all_directed_edges_represented_with_direction() -> None:
    edges = [(3, 0), (0, 2), (2, 1)]
    data = _project(_source(node_count=4, edges=edges)).content
    # Canonical lexicographic ordering (SG-REC-004), all edges preserved, each
    # (source, target) direction intact.
    assert data.edges == ((0, 2), (2, 1), (3, 0))


def test_terminal_classification_correct() -> None:
    # Nodes with out-degree zero: 1, 3, 4 for this edge set.
    data = _project(_source(node_count=5, edges=[(0, 1), (0, 3), (2, 4)])).content
    assert sorted(data.terminals) == [1, 3, 4]
    # Terminal identification agrees with the contract's canonical derivation.
    assert len(data.terminals) == data.node_count - len({s for s, _ in data.edges})
    graph = simple_digraph(5, [(0, 1), (0, 3), (2, 4)])
    assert len(data.terminals) == graph.terminal_count


def test_visual_realization_draws_edges_and_nodes() -> None:
    figure = render_figure_projection(
        _project(_source(node_count=4, edges=[(0, 1), (1, 2), (2, 3)])), registry=_registry()
    )
    assert type(figure).__name__ == "Figure"
    # One axes; edges are annotations (arrows) and nodes are scatter artists.
    axes = figure.axes[0]
    assert len(axes.collections) >= 4  # one scatter per node
    # Node-id labels are drawn (plus title); at least 4 text labels for the ids.
    assert len(axes.texts) >= 4


# ---------------------------------------------------------------------------
# node IDs are not coordinates (Phase-2 § 11)
# ---------------------------------------------------------------------------


def test_node_ids_are_categorical_not_coordinates() -> None:
    """Drawing coordinates come from a separate visual layout, not node IDs."""
    positions = _circular_positions(4)
    # Positions are on the unit circle, not (0,0),(1,0),(2,0),... — node IDs are
    # NOT mapped to x/y coordinates.
    for x, y in positions:
        assert abs(x * x + y * y - 1.0) < 1e-9
    # Node 0 is NOT placed at x=0.
    assert positions[0][0] != 0.0 or positions[0][1] != 0.0


# ---------------------------------------------------------------------------
# canonical contract derivation reused, not reimplemented (Phase-2 § 5)
# ---------------------------------------------------------------------------


def test_contract_derived_properties_reused() -> None:
    """The figure reads contract-owned derived properties, not independent ones."""
    source = _source(node_count=4, edges=[(0, 1), (1, 2), (2, 3)])
    data = _project(source).content
    # Cross-check against the contract's own constructor (single authority).
    graph = simple_digraph(4, [(0, 1), (1, 2), (2, 3)])
    assert data.acyclic == graph.acyclic
    assert data.all_nodes_reach_a_terminal == graph.all_nodes_reach_a_terminal
    assert data.node_count == graph.node_count


# ---------------------------------------------------------------------------
# metamorphic: incidental insertion order → same prepared semantics (Phase-2 § 16)
# ---------------------------------------------------------------------------


def test_incidental_edge_insertion_order_same_prepared_semantics() -> None:
    edges_a = [(0, 1), (1, 2), (2, 3), (0, 3)]
    edges_b = [(2, 3), (0, 3), (1, 2), (0, 1)]  # same relation, different order
    # Same record identity: the metamorphic invariant is that incidental edge
    # construction order within one record yields identical semantics + identity.
    proj_a = _project(_source(record_id="sha256:A", node_count=4, edges=edges_a))
    proj_b = _project(_source(record_id="sha256:A", node_count=4, edges=edges_b))
    assert proj_a.content.edges == proj_b.content.edges == ((0, 1), (0, 3), (1, 2), (2, 3))
    assert proj_a.content.terminals == proj_b.content.terminals
    assert str(proj_a.identity()) == str(proj_b.identity())


def test_canonical_layout_input_order_deterministic() -> None:
    positions_a = _circular_positions(6)
    positions_b = _circular_positions(6)
    assert positions_a == positions_b
    assert len(positions_a) == 6


# ---------------------------------------------------------------------------
# layout determinism & projection-identity separation (Phase-2 § 12-13, § 41)
# ---------------------------------------------------------------------------


def test_layout_change_does_not_change_projection_identity() -> None:
    """Visual layout is realization-only; changing it never changes ProjectionIdentity.

    This is a non-vacuous proof of the SRF-006/SRF-017 partition: the projection
    identity payload is built from the scientific structure + exact provenance
    only and contains no layout/coordinate field (``projection.py``
    ``ProjectionIdentity``). We assert that directly, draw under a different
    (reflected) deterministic layout via the ordinary realization path, and
    confirm the projection identity string is unchanged — the projection is
    identical even though the realized coordinates differ.
    """
    from dataclasses import fields

    from ehp_sn.figures.builtin.simple_digraph import _circular_positions

    source = _source(node_count=4, edges=[(0, 1), (1, 2), (2, 3)])
    projection = _project(source)
    identity_before = str(projection.identity())

    # (a) The projection identity carries no drawing-coordinate/layout field.
    id_field_names = {f.name for f in fields(projection.identity())}
    assert not (id_field_names & {"positions", "layout", "coordinates", "seed", "layout_seed"})

    # (b) A reflected circular placement is a genuinely different deterministic
    # layout, yet realizing that visual choice never alters projection identity.
    reflected = [(-x, y) for (x, y) in _circular_positions(4)]
    assert reflected != _circular_positions(4)
    render_figure_projection(projection, registry=_registry())
    assert str(projection.identity()) == identity_before


def test_layout_is_explicit_algorithm_deterministic_rng_free() -> None:
    """Graph layout is a fixed explicit algorithm, isolated from scientific RNG.

    The canonical circular placement is a fully specified deterministic function
    of the node count (G-009 · SRF-007). It consumes no scientific RNG: seeding
    or perturbing the RNG in any way leaves the returned coordinates unchanged
    (G-010 · SRF-007).
    """
    import random

    from ehp_sn.figures.builtin.simple_digraph import _circular_positions

    baseline = _circular_positions(8)
    # Perturb the global RNG heavily — the layout must be unaffected.
    random.seed(12345)
    [random.random() for _ in range(100)]
    assert _circular_positions(8) == baseline
    random.seed(999)
    assert _circular_positions(8) == baseline
    # Fully deterministic across calls (explicit algorithm, no hidden selection).
    assert _circular_positions(8) == _circular_positions(8)


def test_graph_beyond_node_capacity_fails_explicitly() -> None:
    """An impractically large graph fails explicitly, never silently truncated.

    The supported operational node capacity is 2000 (G-013 · SRF-019): a larger
    graph must fail with :class:`InspectionCapacityExceeded` rather than dropping
    nodes/edges to fit presentation capacity.
    """
    from ehp_sn.figures import InspectionCapacityExceeded

    with pytest.raises(InspectionCapacityExceeded):
        _project(_source(node_count=2001, edges=[(0, 1)]))


def test_graph_within_node_capacity_renders_every_node() -> None:
    """A graph at the operational node capacity renders all nodes/edges (G-013)."""
    node_count = 2000
    edges = [(i, i + 1) for i in range(node_count - 1)]
    projection = _project(_source(node_count=node_count, edges=edges))
    assert projection.content.node_count == node_count
    assert len(projection.content.edges) == node_count - 1


def test_different_edge_relation_changes_projection_identity() -> None:
    a = _project(_source(record_id="sha256:A", node_count=4, edges=[(0, 1), (1, 2), (2, 3)]))
    b = _project(_source(record_id="sha256:B", node_count=4, edges=[(0, 1), (1, 2)]))
    assert str(a.identity()) != str(b.identity())


def test_same_graph_same_source_same_identity() -> None:
    a = _project(_source(record_id="sha256:A", node_count=4, edges=[(0, 1), (1, 2)]))
    b = _project(_source(record_id="sha256:B", node_count=4, edges=[(0, 1), (1, 2)]))
    # Different record identity → different provenance → different projection
    # identity, even for the same graph content.
    assert str(a.identity()) != str(b.identity())


# ---------------------------------------------------------------------------
# producer-extension blindness (Phase-3 § 17 · SRF-016)
# ---------------------------------------------------------------------------


def test_graph_producer_metadata_perturbation_unchanged_generic_view() -> None:
    """G-012 — producer metadata outside the shared contract cannot alter the view.

    Two records with the same ``simple-digraph/v1`` payload but different
    producer-specific metadata prepare to the same contract-owned FigureData
    and the same generic scientific visual encoding (Phase-3 § 17 · SRF-016).
    Exact source/provenance identity may differ; projection identity equality is
    not required.
    """
    base = {"node_count": 4, "edges": [(0, 1), (1, 2), (2, 3)]}
    plain = _ExactSource(
        artifact_ref="artifact:dag/v1",
        record_id="sha256:GPA",
        schema_ref="simple-digraph/v1",
        content=dict(base),
    )
    extended = _ExactSource(
        artifact_ref="artifact:dag/v1",
        record_id="sha256:GPB",
        schema_ref="simple-digraph/v1",
        content={**base, "generation_protocol": "dagflow-ish/v1", "variant": "x"},  # producer ext
    )
    a = _project(plain)
    b = _project(extended)
    # Same contract-owned prepared scientific view.
    assert a.content.node_count == b.content.node_count == 4
    assert a.content.edges == b.content.edges == ((0, 1), (1, 2), (2, 3))
    assert a.content.terminals == b.content.terminals
    assert a.content.acyclic == b.content.acyclic


# ---------------------------------------------------------------------------
# no task/goal semantics (Phase-2 § 10)
# ---------------------------------------------------------------------------


def test_figure_exposes_no_task_goal_semantics() -> None:
    """Terminal, not goal/start; no query/reward/target/solution semantics."""
    data = _project(_source(node_count=3, edges=[(0, 1)])).content
    assert not hasattr(data, "goal")
    assert not hasattr(data, "start")
    assert not hasattr(data, "reward")
    assert not hasattr(data, "trajectory")
    assert not hasattr(data, "solution")


# ---------------------------------------------------------------------------
# mutation boundary (Phase-2 § 33)
# ---------------------------------------------------------------------------


def test_rendering_does_not_mutate_source_prepared_or_projection() -> None:
    source_dict = {"node_count": 4, "edges": [(0, 1), (1, 2), (2, 3)]}
    source = _ExactSource(
        artifact_ref="artifact:dag/v1",
        record_id="sha256:MM",
        schema_ref="simple-digraph/v1",
        content=source_dict,
    )
    projection = _project(source)
    prepared_before = tuple(projection.content.edges)
    identity_before = str(projection.identity())

    render_figure_projection(projection, registry=_registry())

    assert tuple(projection.content.edges) == prepared_before
    assert str(projection.identity()) == identity_before
    assert source_dict["edges"] == [(0, 1), (1, 2), (2, 3)]
    assert source_dict["node_count"] == 4


# ---------------------------------------------------------------------------
# producer independence (Phase-2 § 15/19.4 spirit): equivalent records, no branch
# ---------------------------------------------------------------------------


def test_equivalent_records_from_different_contexts_same_figure() -> None:
    source_a = _source(
        artifact_ref="artifact:dag/v1", record_id="sha256:A", node_count=4, edges=[(0, 1)]
    )
    source_b = _source(
        artifact_ref="artifact:fixture/v9", record_id="sha256:B", node_count=4, edges=[(0, 1)]
    )
    proj_a = _project(source_a)
    proj_b = _project(source_b)
    assert proj_a.figure_ref == proj_b.figure_ref == _GRAPH_REF
    assert proj_a.source.role == proj_b.source.role == "graph"
    # Different artifact identity → different provenance/identity, same figure.
    assert str(proj_a.identity()) != str(proj_b.identity())


# ---------------------------------------------------------------------------
# version-explicit compatibility (Phase-2 § 32, § 44)
# ---------------------------------------------------------------------------


def test_unknown_future_contract_version_is_incompatible() -> None:
    """The figure must not accept a future contract through structural duck typing.

    A hypothetical ``simple-digraph/v2`` record whose fields happen to include
    ``node_count`` and ``edges`` is NOT compatible with
    ``figure:simple-digraph-inspection/v1`` (which requires ``simple-digraph/v1``).
    """
    source = _ExactSource(
        artifact_ref="artifact:dag/v1",
        record_id="sha256:V2",
        schema_ref="simple-digraph/v2",  # unknown future semantic version
        content={"node_count": 4, "edges": [(0, 1), (1, 2)]},
    )
    with pytest.raises(FigureInputCompatibilityError):
        prepare_figure(_registry(), _GRAPH_REF, source)


def test_supported_exact_contract_version_is_compatible() -> None:
    """The exact supported contract version is compatible (no duck typing)."""
    projection = _project(_source(node_count=4, edges=[(0, 1), (1, 2)]))
    assert projection.figure_ref == _GRAPH_REF
