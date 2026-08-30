"""Artifact-summary producer independence (Phase-4 § 28 · P4-ARCH-001).

These test that the three framework-owned artifact-scale summary figures are
producer-independent at the record-content level: a record carrying
producer-extension metadata (generator profile, region id, assignment protocol,
seed) that does not belong to the shared logical contract yields the identical
generic prepared view as a bare contract-conforming record.

This is the Phase-4 H4-2 claim — compatibility is determined by the logical
contract and the figure's declared input requirement, never by ``producer ==
...`` — exercised at the record-reconstruction boundary each summary uses
(``projection.md`` § "Source roles"; Phase-4 § 28).
"""

from __future__ import annotations

from ehp_sn.contracts.domains import rectangular_row_column_domain
from ehp_sn.contracts.observations import AnonymousVocabulary, categorical_field
from ehp_sn.contracts.relations import simple_digraph
from ehp_sn.contracts.topology import raster_topology
from ehp_sn.figures.builtin.categorical_field_artifact_summary import (
    _reconstruct_field,
)
from ehp_sn.figures.builtin.raster_topology_artifact_summary import (
    _reconstruct_topology,
)
from ehp_sn.figures.builtin.simple_digraph_artifact_summary import (
    _reconstruct_digraph,
)


def test_graph_summary_ignores_producer_extensions():
    """A producer-extension record with extra non-contract metadata yields the
    same generic reconstruction as the bare contract record (Phase-4 § 28)."""
    bare = simple_digraph(3, [(0, 1), (1, 2)])
    extended = {
        "node_count": 3,
        "edges": [[0, 1], [1, 2]],
        "generator_profile": "variant-7",
        "generation_seed": 42,
    }
    assert _reconstruct_digraph(extended).content() == bare.content()


def test_raster_summary_ignores_producer_extensions():
    """A producer-extension raster record with a non-contract ``region_id``
    reconstructs identically to the bare contract record (Phase-4 § 28)."""
    d = rectangular_row_column_domain(2, 3)
    bare = raster_topology(d, [1, 0, 1, 1, 0, 1])
    extended = {
        "extent": {"height": 2, "width": 3, "position_count": 6, "schema": "rectangular-row-column/v1"},
        "passable": [True, False, True, True, False, True],
        "region_id": "some-region",
    }
    assert _reconstruct_topology(extended).content() == bare.content()


def test_field_summary_ignores_producer_extensions():
    """A producer-extension categorical record with assignment metadata
    reconstructs identically to the bare contract record (Phase-4 § 28)."""
    d = rectangular_row_column_domain(1, 2)
    v = AnonymousVocabulary(identity="v", cardinality=2)
    bare = categorical_field(d, v, [0, 1])
    extended = {
        "domain": {"schema": "rectangular-row-column/v1", "height": 1, "width": 2, "position_count": 2},
        "vocabulary": {"kind": "anonymous", "identity": "v", "cardinality": 2},
        "observation_id": [0, 1],
        "assignment_protocol": "some-protocol",
        "realization_index": 3,
    }
    assert _reconstruct_field(extended).content() == bare.content()
