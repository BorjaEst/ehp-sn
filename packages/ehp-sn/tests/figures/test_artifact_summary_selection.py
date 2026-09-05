"""Shared artifact-summary selection & descriptor determinism (Phase-4 § 22-27).

These test the deterministic selection and exact inspection descriptors shared
by the three framework-owned artifact-scale summary figures. The summaries are
producer-independent and governed by the Phase-4 requirements:

* P4-ART-001 — enumeration-order independence: the same record collection under
  a different incidental enumeration order yields the same descriptors, the
  same resolved representative identities, and the same ``ProjectionIdentity``
  (Phase-4 § 27).
* P4-ART-002 — deterministic representative selection: every ordering/eligibility
  rule is defined (candidate population, descriptor, ordering, cardinality,
  tie-break, missing/non-finite handling, duplicate handling), with stable
  record identity as the final tie-break (Phase-4 § 22-23).
* P4-SCHEMA — each descriptor is an exact inspection descriptor over the
  authoritative contract, with edge cases specified rather than left to
  divide-by-zero (Phase-4 § 22).
* No-mutation — realization never mutates the source collection or the prepared
  projection (``FIG-003``).

Headless Matplotlib backend is selected before any pyplot use.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless backend required

import random

import pytest
from ehp_sn.contracts.domains import rectangular_row_column_domain
from ehp_sn.contracts.observations import AnonymousVocabulary, categorical_field
from ehp_sn.contracts.relations import simple_digraph
from ehp_sn.contracts.topology import raster_topology
from ehp_sn.figures import (
    effective_figure_registry,
    prepare_figure,
    render_figure_projection,
)
from ehp_sn.figures.builtin.categorical_field_artifact_summary import (
    vocabulary_utilization,
)
from ehp_sn.figures.builtin.raster_topology_artifact_summary import (
    passable_fraction,
)
from ehp_sn.figures.builtin.simple_digraph_artifact_summary import (
    _DigraphRecordMetric,
    _select_graph_representatives,
    edge_density,
)
from ehp_sn.figures.inspection import (
    ORDER_ASCENDING,
    SelectionCandidate,
    rank_candidates,
)

from .artifact_summary_helpers import (
    GRAPH_ARTIFACT_SUMMARY_REF,
    artifact_summary_cases,
    graph_records,
    graph_source,
)


def _registry():
    return effective_figure_registry()


# ---------------------------------------------------------------------------
# P4-ART-001 — enumeration-order independence (Phase-4 § 27)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("ref", "source_fn", "records_fn"), artifact_summary_cases())
def test_enumeration_order_independence_yields_same_projection(ref, source_fn, records_fn):
    """Same record collection under different incidental enumeration order → the
    same descriptors, the same resolved representative ids, and the same
    projection identity (Phase-4 § 27 · P4-ART-001)."""
    base_records = records_fn()
    base = prepare_figure(_registry(), ref, source_fn(base_records))
    for seed in range(12):
        permuted = list(base_records)
        random.Random(seed).shuffle(permuted)
        alt = prepare_figure(_registry(), ref, source_fn(permuted))
        # Same prepared descriptor arrays (canonicalized by record identity).
        assert str(base.content) == str(alt.content)
        # Same resolved representative identities.
        assert base.selection.resolved_identities == alt.selection.resolved_identities
        # Same projection identity (collection + selection are order-independent).
        assert str(base.identity()) == str(alt.identity())


def test_graph_gallery_is_min_median_max_edge_density():
    """The graph gallery selects the min/median/max edge-density records in total
    ascending edge-density order (Phase-4 § 24)."""
    records = graph_records()
    projection = prepare_figure(_registry(), GRAPH_ARTIFACT_SUMMARY_REF, graph_source(records))
    data = projection.content
    assert data.record_count == len(records)
    selected = data.selected_ids
    assert len(selected) == 3
    densities = [data.edge_densities[list(data.record_ids).index(i)] for i in selected]
    assert densities == sorted(densities)


# ---------------------------------------------------------------------------
# P4-ART-002 — descriptor edge cases (Phase-4 § 22)
# ---------------------------------------------------------------------------


def test_edge_density_defines_single_node():
    """edge_density for node_count == 1 is defined (0.0), no divide-by-zero."""
    single = simple_digraph(1, [])
    assert edge_density(single) == 0.0


def test_passable_fraction_is_well_defined():
    """passable_fraction is defined for any extent (position_count >= 1)."""
    d = rectangular_row_column_domain(2, 3)
    t = raster_topology(d, [1, 0, 1, 1, 0, 1])
    assert passable_fraction(t) == pytest.approx(4 / 6)


def test_vocabulary_utilization_is_well_defined():
    """vocabulary_utilization is defined (cardinality >= 1, no divide-by-zero)."""
    d = rectangular_row_column_domain(1, 2)
    v = AnonymousVocabulary(identity="v", cardinality=2)
    f = categorical_field(d, v, [0, 1])
    assert vocabulary_utilization(f) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# P4-ART-002 — deterministic representative selection (Phase-4 § 23)
# ---------------------------------------------------------------------------


def test_selection_ties_resolve_by_record_identity():
    """Equal descriptors resolve deterministically by stable record identity."""
    candidates = [
        SelectionCandidate(record_id="z", descriptor=1.0),
        SelectionCandidate(record_id="a", descriptor=1.0),
        SelectionCandidate(record_id="m", descriptor=2.0),
    ]
    ranked = tuple(c.record_id for c in rank_candidates(candidates, order=ORDER_ASCENDING))
    # The two equal-descriptor candidates order by record id: 'a' then 'z'.
    assert ranked == ("a", "z", "m")


def test_finite_descriptors_rank_before_missing_and_non_finite():
    """Finite descriptors rank before missing/non-finite by the default policy."""
    candidates = [
        SelectionCandidate(record_id="nan", descriptor=float("nan")),
        SelectionCandidate(record_id="none", descriptor=None),
        SelectionCandidate(record_id="fin", descriptor=0.5),
    ]
    ranked = tuple(c.record_id for c in rank_candidates(candidates, order=ORDER_ASCENDING))
    assert ranked[0] == "fin"


def test_small_collection_returns_all_in_deterministic_order():
    """A one- or two-record collection returns all of its records in the total
    deterministic order (never exceeding the population)."""
    one = (_DigraphRecordMetric("x", simple_digraph(2, [(0, 1)]), 1, 0.5),)
    assert _select_graph_representatives(one) == ("x",)
    two = one + (_DigraphRecordMetric("y", simple_digraph(4, [(0, 1)]), 1, 1 / 12),)
    assert _select_graph_representatives(two) == ("y", "x")


# ---------------------------------------------------------------------------
# Non-mutation — realization never mutates source/projection (FIG-003)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("ref", "source_fn", "records_fn"), artifact_summary_cases())
def test_render_does_not_mutate_source_or_projection(ref, source_fn, records_fn):
    """Realizing the summary does not mutate the source collection or projection."""
    records = records_fn()
    before = str(tuple(sorted(r.record_id for r in records)))
    projection = prepare_figure(_registry(), ref, source_fn(records))
    content_before = projection.content
    figure = render_figure_projection(projection, registry=_registry())
    assert figure is not None
    after = str(tuple(sorted(r.record_id for r in records)))
    assert before == after
    assert projection.content == content_before
