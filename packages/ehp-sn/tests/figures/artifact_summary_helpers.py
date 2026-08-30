"""Shared helpers for framework artifact-summary figure tests.

These producer-neutral collection builders are shared by the artifact-summary
figure test modules (selection/determinism, genericity, categorical semantics,
scope). They are not collected as tests. They build in-memory ``LogicalRecord``
collections and generic ``_CollectionSource`` objects through the ordinary
contract constructors — never a producer identity (Phase-4 § 19-20).
"""

from __future__ import annotations

from ehp_sn.contracts.domains import rectangular_row_column_domain
from ehp_sn.contracts.observations import AnonymousVocabulary, categorical_field
from ehp_sn.contracts.relations import simple_digraph
from ehp_sn.contracts.topology import raster_topology
from ehp_sn.execution import LogicalRecord
from ehp_sn.figures.builtin.categorical_field_artifact_summary import (
    CATEGORICAL_FIELD_ARTIFACT_SUMMARY_REF,
)
from ehp_sn.figures.builtin.raster_topology_artifact_summary import (
    RASTER_TOPOLOGY_ARTIFACT_SUMMARY_REF,
)
from ehp_sn.figures.builtin.simple_digraph_artifact_summary import (
    SIMPLE_DIGRAPH_ARTIFACT_SUMMARY_REF,
)
from ehp_sn.figures.service import _CollectionSource

#: Canonical references of the three built-in artifact-summary figures.
GRAPH_ARTIFACT_SUMMARY_REF = SIMPLE_DIGRAPH_ARTIFACT_SUMMARY_REF
RASTER_ARTIFACT_SUMMARY_REF = RASTER_TOPOLOGY_ARTIFACT_SUMMARY_REF
FIELD_ARTIFACT_SUMMARY_REF = CATEGORICAL_FIELD_ARTIFACT_SUMMARY_REF

#: Canonical record scope of the ordinary record inspectors.
GRAPH_INSPECTION_REF = "figure:simple-digraph-inspection/v1"


def record(record_id: str, schema_ref: str, content: object) -> LogicalRecord:
    """Build one logical record with no descriptors."""
    return LogicalRecord(record_id=record_id, schema_ref=schema_ref, content=content, descriptors=())


def graph_records() -> list[LogicalRecord]:
    """A producer-neutral ``simple-digraph/v1`` collection."""
    return [
        record("g1", "simple-digraph/v1", simple_digraph(2, [(0, 1)]).content()),
        record("g2", "simple-digraph/v1", simple_digraph(4, [(0, 1)]).content()),
        record("g3", "simple-digraph/v1", simple_digraph(3, [(0, 1), (1, 2)]).content()),
        record("g4", "simple-digraph/v1", simple_digraph(3, [(0, 1), (1, 2), (2, 0)]).content()),
    ]


def raster_records() -> list[LogicalRecord]:
    """A producer-neutral ``raster-topology/v1`` collection."""
    d1 = rectangular_row_column_domain(2, 3)
    d2 = rectangular_row_column_domain(3, 3)
    return [
        record(
            "r1",
            "raster-topology/v1",
            raster_topology(d1, [True, False, True, True, False, True]).content(),
        ),
        record("r2", "raster-topology/v1", raster_topology(d2, [True] * 9).content()),
        record(
            "r3",
            "raster-topology/v1",
            raster_topology(d1, [True, True, False, False, True, False]).content(),
        ),
    ]


def field_records() -> list[LogicalRecord]:
    """A producer-neutral ``categorical-field/v1`` collection with two vocabularies."""
    d1 = rectangular_row_column_domain(2, 3)
    d2 = rectangular_row_column_domain(3, 3)
    v1 = AnonymousVocabulary(identity="vocab-a", cardinality=3)
    v2 = AnonymousVocabulary(identity="vocab-b", cardinality=2)
    return [
        record("f1", "categorical-field/v1", categorical_field(d1, v1, [0, 1, 2, 0, 1, 2]).content()),
        record(
            "f2",
            "categorical-field/v1",
            categorical_field(d2, v1, [0, 1, 2, 0, 1, 2, 0, 1, 2]).content(),
        ),
        record("f3", "categorical-field/v1", categorical_field(d1, v2, [0, 1, 0, 1, 0, 1]).content()),
    ]


def graph_source(records) -> _CollectionSource:
    """A generic artifact-scope ``simple-digraph/v1`` collection source."""
    return _CollectionSource(
        artifact_ref="artifact:dag/v1",
        schema_ref="simple-digraph/v1",
        records=tuple(records),
        content=tuple(records),
    )


def raster_source(records) -> _CollectionSource:
    """A generic artifact-scope ``raster-topology/v1`` collection source."""
    return _CollectionSource(
        artifact_ref="artifact:raster/v1",
        schema_ref="raster-topology/v1",
        records=tuple(records),
        content=tuple(records),
    )


def field_source(records) -> _CollectionSource:
    """A generic artifact-scope ``categorical-field/v1`` collection source."""
    return _CollectionSource(
        artifact_ref="artifact:field/v1",
        schema_ref="categorical-field/v1",
        records=tuple(records),
        content=tuple(records),
    )


def artifact_summary_cases():
    """Parametrized ``(ref, source_builder, records_builder)`` for each summary.

    Lets shared tests (order-invariance, non-mutating rendering) run once per
    summary figure, mirroring how the three summary figures share one generic
    framework path (Phase-4 § 19-20).
    """
    return [
        (GRAPH_ARTIFACT_SUMMARY_REF, graph_source, graph_records),
        (RASTER_ARTIFACT_SUMMARY_REF, raster_source, raster_records),
        (FIELD_ARTIFACT_SUMMARY_REF, field_source, field_records),
    ]


__all__ = [
    "FIELD_ARTIFACT_SUMMARY_REF",
    "GRAPH_ARTIFACT_SUMMARY_REF",
    "GRAPH_INSPECTION_REF",
    "RASTER_ARTIFACT_SUMMARY_REF",
    "artifact_summary_cases",
    "field_records",
    "field_source",
    "graph_records",
    "graph_source",
    "raster_records",
    "raster_source",
    "record",
]
