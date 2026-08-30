"""Record-rendering capacity characterization (Phase 2 § 30-31).

These tests characterize basic rendering behaviour for increasing valid record
sizes to expose obvious pathological implementation behaviour, and verify the
complete-or-explicit-failure renderability invariant (Phase-2 § 30):

* within supported operational rendering capacity, the complete scientific
  record is rendered — no silent node/edge/cell dropping, sampling, or
  truncation of scientific content;
* increasing valid graph and field sizes are exercised (Phase-2 § 31).

This is an operational validation target, not scientific acceptance evidence and
not a performance budget. It asserts no accidental *unbounded* behaviour is
hidden behind a happy-path fixture and that scientific content is never
silently omitted to fit a rendering budget.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless backend required

from ehp_sn.contracts.domains import rectangular_row_column_domain
from ehp_sn.contracts.observations import AnonymousVocabulary, categorical_field
from ehp_sn.figures import (
    effective_figure_registry,
    prepare_figure,
    render_figure_projection,
)
from ehp_sn.figures.service import _ExactSource

_GRAPH_REF = "figure:simple-digraph-inspection/v1"
_FIELD_REF = "figure:categorical-field-inspection/v1"


def _graph_source(node_count: int, edges) -> _ExactSource:
    return _ExactSource(
        artifact_ref="artifact:dag/v1",
        record_id=f"sha256:G{node_count}",
        schema_ref="simple-digraph/v1",
        content={"node_count": node_count, "edges": list(edges)},
    )


def _field_source(height: int, width: int, cardinality: int) -> _ExactSource:
    domain = rectangular_row_column_domain(height, width)
    vocab = AnonymousVocabulary(identity=f"v-k{cardinality}", cardinality=cardinality)
    ids = [i % cardinality for i in range(domain.position_count)]
    field = categorical_field(domain, vocab, ids)
    return _ExactSource(
        artifact_ref="artifact:obs/v1",
        record_id=f"sha256:F{height}x{width}",
        schema_ref="categorical-field/v1",
        content=field.content(),
    )


def test_increasing_graph_sizes_are_rendered_completely() -> None:
    """Larger contract-valid graphs still render every node and edge."""
    registry = effective_figure_registry()
    for node_count in (10, 50, 100):
        # A chain graph: node_count-1 edges, every node represented.
        edges = [(i, i + 1) for i in range(node_count - 1)]
        projection = prepare_figure(registry, _GRAPH_REF, _graph_source(node_count, edges))
        data = projection.content
        assert data.node_count == node_count
        assert len(data.edges) == node_count - 1
        figure = render_figure_projection(projection, registry=registry)
        assert type(figure).__name__ == "Figure"


def test_high_edge_count_graph_renders_all_edges() -> None:
    """A dense graph renders every edge and node with no truncation."""
    registry = effective_figure_registry()
    node_count = 40
    edges = [(i, j) for i in range(node_count) for j in range(node_count) if i != j and (i, j) < (j, i)]
    projection = prepare_figure(registry, _GRAPH_REF, _graph_source(node_count, edges))
    assert projection.content.node_count == node_count
    assert len(projection.content.edges) == len(edges)
    figure = render_figure_projection(projection, registry=registry)
    assert type(figure).__name__ == "Figure"


def test_increasing_field_sizes_are_rendered_completely() -> None:
    """Larger categorical fields render every position (no cell dropping)."""
    registry = effective_figure_registry()
    for height, width in ((5, 5), (10, 10), (20, 20)):
        projection = prepare_figure(registry, _FIELD_REF, _field_source(height, width, cardinality=3))
        data = projection.content
        expected = height * width
        assert len(data.observation_ids) == expected
        figure = render_figure_projection(projection, registry=registry)
        assert type(figure).__name__ == "Figure"


def test_high_cardinality_large_field_renders_completely() -> None:
    """High vocabulary cardinality over a large field still renders all positions."""
    registry = effective_figure_registry()
    projection = prepare_figure(registry, _FIELD_REF, _field_source(12, 12, cardinality=200))
    data = projection.content
    assert len(data.observation_ids) == 144  # no loss
    assert data.represented_category_count <= 200
    figure = render_figure_projection(projection, registry=registry)
    assert type(figure).__name__ == "Figure"
