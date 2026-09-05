"""Tests for Maze-ND lineage, exact equality, and dedup (Targets 6-8).

Covers stable source-occurrence identity (independent of ordering), exact
normalized-topology equality (extent + passability only), duplicate aggregation
(3 equal rows -> 1 topology + 3-occurrence lineage), complete many-to-one
lineage, bounded per-record summaries, source-split overlap reporting, and the
absence of any rotation/reflection/compact-state/first-occurrence dedup.
"""

from __future__ import annotations

import pytest
from ehp_research.substrates.maze_nd.extraction import extract_row
from ehp_research.substrates.maze_nd.lineage import (
    SourceOccurrenceIdentity,
    TopologyGroup,
    build_lineage_resource,
    group_source_occurrences,
    normalized_topology_key,
    occurrence_identity,
)

from . import _fixtures as fx

REVISION = "rev-fixed"


def _extracted(*rows: str, split: str = "train.jsonl.gz", ordinal: int = 0):
    return extract_row(fx.row(fx.grid_from_strings(*rows)), split_file=split, row_ordinal=ordinal)


def _qrow(*rows: str, split: str = "train.jsonl.gz", ordinal: int = 0):
    ext = _extracted(*rows, split=split, ordinal=ordinal)
    identity = occurrence_identity(ext, source_revision=REVISION)
    return (ext.height, ext.width, ext.passable, identity, ext.source_metadata)


def test_normalized_topology_key_is_extent_and_passability_only() -> None:
    key = normalized_topology_key(2, 3, (True, False, False, True, False, False))
    assert key == (2, 3, (True, False, False, True, False, False))


def test_occurrence_identity_is_deterministic_and_not_topology_id() -> None:
    a = SourceOccurrenceIdentity(REVISION, "train.jsonl.gz", 0)
    b = SourceOccurrenceIdentity(REVISION, "train.jsonl.gz", 0)
    assert a == b
    assert a.canonical() == "rev-fixed::train.jsonl.gz::0"
    # Same topology but different source row gives a different occurrence identity.
    assert a != SourceOccurrenceIdentity(REVISION, "train.jsonl.gz", 1)


def test_equal_source_rows_group_into_one_topology() -> None:
    # Three equal normalized topologies spanning two source splits.
    rows = [
        _qrow("#S#", "#G#", split="train.jsonl.gz", ordinal=0),
        _qrow("#S#", "#G#", split="train.jsonl.gz", ordinal=5),
        _qrow("#S#", "#G#", split="test.jsonl.gz", ordinal=2),
    ]
    groups = group_source_occurrences(rows)
    assert len(groups) == 1
    group = groups[0]
    assert isinstance(group, TopologyGroup)
    assert group.occurrence_count == 3
    assert group.source_split_labels == ("test", "train")
    assert group.spans_multiple_splits is True


def test_distinct_topologies_stay_distinct() -> None:
    rows = [
        _qrow("#S#", "#G#"),  # 2x3, passability pattern P1
        _qrow("## ", "## "),  # 2x3, passability pattern P2 (distinct)
        _qrow("##", "#S", "##"),  # 3x2, distinct extent
    ]
    groups = group_source_occurrences(rows)
    assert len(groups) == 3


def test_rotation_not_merged() -> None:
    """Rotation/reflection equivalence is NOT used for dedup."""
    rows = [
        _qrow("#S", "  "),
        _qrow("  ", "#S"),
    ]
    groups = group_source_occurrences(rows)
    assert len(groups) == 2


def test_complete_many_to_one_lineage_preserves_all_occurrences() -> None:
    rows = [
        _qrow("#S#", "#G#", split="train.jsonl.gz", ordinal=0),
        _qrow("#S#", "#G#", split="train.jsonl.gz", ordinal=7),
        _qrow("#S#", "#G#", split="test.jsonl.gz", ordinal=3),
        _qrow("## ", "## ", split="train.jsonl.gz", ordinal=9),
    ]
    groups = group_source_occurrences(rows)
    # Assign framework record_ids by key.
    record_ids = {g.key: f"record-{i}" for i, g in enumerate(groups)}
    resource = build_lineage_resource(groups, source_revision=REVISION, record_ids=record_ids)

    occ_to_record = resource["occurrence_to_record"]
    # Every source occurrence is present (no duplicate disappears).
    assert len(occ_to_record) == 4
    assert occ_to_record["rev-fixed::train.jsonl.gz::0"] == "record-0"
    assert occ_to_record["rev-fixed::train.jsonl.gz::7"] == "record-0"
    assert occ_to_record["rev-fixed::test.jsonl.gz::3"] == "record-0"

    # Bounded summaries: occurrence count + split set (not the full mapping).
    summary = next(s for s in resource["record_summaries"] if s["record_id"] == "record-0")
    assert summary["occurrence_count"] == 3
    assert set(summary["source_split_labels"]) == {"train", "test"}
    assert summary["lineage_resource"] == "source-lineage"

    # Source-split overlap reported for the topology spanning train+test.
    assert resource["source_split_overlap_records"] == ["record-0"]


def test_lineage_summary_is_bounded() -> None:
    """No summary embeds the unbounded list of source-row references."""
    rows = [_qrow("#S#", "#G#", split="train.jsonl.gz", ordinal=i) for i in range(5)]
    groups = group_source_occurrences(rows)
    record_ids = {g.key: "record-x" for g in groups}
    resource = build_lineage_resource(groups, source_revision=REVISION, record_ids=record_ids)
    summary = resource["record_summaries"][0]
    assert set(summary.keys()) == {
        "record_id",
        "occurrence_count",
        "source_split_labels",
        "lineage_resource",
    }


def test_occurrence_order_does_not_change_group_identity() -> None:
    """Reordering encountered duplicates yields the same group topology identity."""
    g1 = group_source_occurrences([_qrow("#S#", "#G#", ordinal=9), _qrow("#S#", "#G#", ordinal=0)])
    g2 = group_source_occurrences([_qrow("#S#", "#G#", ordinal=0), _qrow("#S#", "#G#", ordinal=9)])
    assert g1[0].key == g2[0].key
    assert {o.identity.canonical() for o in g1[0].occurrences} == {
        o.identity.canonical() for o in g2[0].occurrences
    }
