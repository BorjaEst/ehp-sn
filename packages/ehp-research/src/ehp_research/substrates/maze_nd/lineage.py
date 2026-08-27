"""Maze-ND source-occurrence lineage and exact normalized-topology grouping.

This module owns the Maze-ND mapping from source problem occurrences to unique
normalized topology records, and the separate complete many-to-one lineage
resource. It implements:

* :func:`SourceOccurrenceIdentity` — a deterministic identity for every source
  row that is independent of filesystem enumeration, iteration order, worker
  scheduling, and the first duplicate encountered;
* :func:`normalized_topology_key` — the exact Maze-ND topology equality:
  same normalized extent AND same cell-wise passability in preserved
  orientation, and nothing else;
* duplicate aggregation — all selected source occurrences yielding the same
  normalized topology map to one record;
* complete many-to-one lineage outside the common raster payload, plus a
  bounded per-record lineage summary.

Maze-ND never deduplicates using graph isomorphism, rotation/reflection
equivalence, compact state arrays, movement tables, source row ID, or first
occurrence. The occurrence identity uses the immutable source revision plus the
source row identity (split file + 0-based row ordinal); it is deliberately
**not** the normalized topology ``record_id``, because one normalized topology
may correspond to many source occurrences.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any

from .extraction import ExtractedTopology
from .source import SPLIT_LABELS

#: The deduplication policy reference (exact oriented raster equality).
DEDUPLICATION_POLICY: str = "maze-nd:dedup/orientation-preserving-raster/v1"


class LineageError(ValueError):
    """A controlled Maze-ND lineage-construction failure."""


def normalized_topology_key(
    height: int, width: int, passable: tuple[bool, ...]
) -> tuple[int, int, tuple[bool, ...]]:
    """Return the exact normalized-topology equality key.

    Equality is exactly: same normalized extent ``(height, width)`` AND same
    cell-wise passability in preserved orientation. Rotation/reflection
    equivalence, compact state arrays, movement tables, and source row identity
    never participate.
    """
    if len(passable) != height * width:
        raise LineageError(
            f"normalized topology key passability length {len(passable)} does not "
            f"match extent {height}x{width}"
        )
    return (height, width, passable)


@dataclass(frozen=True, slots=True)
class SourceOccurrenceIdentity:
    """Deterministic identity of one source problem row in the immutable revision.

    ``source_revision`` pins the immutable source coordinate; ``split_file`` and
    ``row_ordinal`` identify the exact row within it. This is independent of
    enumeration order, worker scheduling, and which duplicate was encountered
    first. It is not the normalized topology ``record_id``.
    """

    source_revision: str
    split_file: str
    row_ordinal: int

    @property
    def split_label(self) -> str:
        """The source split label derived from file membership."""
        return SPLIT_LABELS[self.split_file]

    def canonical(self) -> str:
        """A stable canonical string form of the occurrence identity."""
        return f"{self.source_revision}::{self.split_file}::{self.row_ordinal}"


def occurrence_identity(
    extracted: ExtractedTopology, *, source_revision: str
) -> SourceOccurrenceIdentity:
    """Return the occurrence identity for one validated extracted source row."""
    return SourceOccurrenceIdentity(
        source_revision=source_revision,
        split_file=extracted.split_file,
        row_ordinal=extracted.row_ordinal,
    )


@dataclass(frozen=True, slots=True)
class OccurrenceRecord:
    """One source occurrence with its identity and carried source metadata."""

    identity: SourceOccurrenceIdentity
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class TopologyGroup:
    """One unique normalized topology and all source occurrences mapping to it.

    ``key`` is the exact normalized-topology equality key; ``occurrences`` are
    the complete recorded source occurrences in canonical encounter order. The
    group is keyed by topology content, never by the first-occurrence row.
    """

    key: tuple[int, int, tuple[bool, ...]]
    occurrences: tuple[OccurrenceRecord, ...] = field(default_factory=tuple)

    @property
    def height(self) -> int:
        return self.key[0]

    @property
    def width(self) -> int:
        return self.key[1]

    @property
    def passable(self) -> tuple[bool, ...]:
        return self.key[2]

    @property
    def occurrence_count(self) -> int:
        return len(self.occurrences)

    @property
    def source_split_labels(self) -> tuple[str, ...]:
        """The sorted distinct source split labels represented by occurrences."""
        return tuple(sorted({occ.identity.split_label for occ in self.occurrences}))

    @property
    def spans_multiple_splits(self) -> bool:
        """Whether the group's occurrences span more than one source split."""
        return len(self.source_split_labels) > 1


def group_source_occurrences(
    extracted_rows: list[tuple[int, int, tuple[bool, ...], SourceOccurrenceIdentity, dict[str, Any]]],
) -> tuple[TopologyGroup, ...]:
    """Group selected source occurrences into unique normalized topology groups.

    ``extracted_rows`` is a canonical list of
    ``(height, width, passable, occurrence_identity, source_metadata)`` values in
    encounter order. Equal normalized topologies (exact extent + passability)
    are grouped; encounter order within a group reflects the deterministic
    source order but never affects the group's topology identity.

    Returns the distinct groups in first-encounter order of their topology key.
    """
    groups: OrderedDict[tuple[int, int, tuple[bool, ...]], list[OccurrenceRecord]] = OrderedDict()
    for height, width, passable, identity, metadata in extracted_rows:
        key = normalized_topology_key(height, width, passable)
        groups.setdefault(key, []).append(OccurrenceRecord(identity=identity, metadata=metadata))
    return tuple(TopologyGroup(key=key, occurrences=tuple(records)) for key, records in groups.items())


def lineage_summary(group: TopologyGroup, *, record_id: str) -> dict[str, Any]:
    """Return the bounded JSON-compatible lineage summary for one topology record.

    The summary contains the normalized topology record ID, the occurrence
    count, the set of source split labels represented, and a reference to the
    complete lineage resource. It is bounded and does not embed the unbounded
    list of source-row references into the task-facing topology payload.
    """
    return {
        "record_id": record_id,
        "occurrence_count": group.occurrence_count,
        "source_split_labels": list(group.source_split_labels),
        "lineage_resource": "source-lineage",
    }


def build_lineage_resource(
    groups: tuple[TopologyGroup, ...],
    *,
    source_revision: str,
    record_ids: dict[tuple[int, int, tuple[bool, ...]], str],
    connectivity_policy: str = "preserve",
    rejected_occurrence_count: int = 0,
) -> dict[str, Any]:
    """Build the complete JSON-compatible multi-source-occurrence lineage resource.

    The resource maps every source occurrence (by canonical identity) to the
    normalized topology record it contributes to, and per-record summaries. It
    is the *complete* many-to-one mapping required — no duplicate
    source occurrence disappears — stored in a separate logical lineage
    resource rather than embedded in the common raster payload.

    ``record_ids`` maps each normalized topology key to its framework-derived
    ``record_id``. Under an explicit ``reject`` connectivity policy, the number
    of source occurrences rejected (never silently repaired) is recorded as a
    diagnostic so rejection is not silent.
    """
    occurrence_map: dict[str, str] = {}
    summaries: list[dict[str, Any]] = []
    overlaps: list[str] = []
    for group in groups:
        record_id = record_ids[group.key]
        for occ in group.occurrences:
            occurrence_map[occ.identity.canonical()] = record_id
        summaries.append(lineage_summary(group, record_id=record_id))
        if group.spans_multiple_splits:
            overlaps.append(record_id)

    return {
        "source_revision": source_revision,
        "resource": "source-lineage",
        "schema": "maze-nd:lineage/v1",
        "occurrence_to_record": occurrence_map,
        "record_summaries": summaries,
        "source_split_overlap_records": overlaps,
        "connectivity_policy": connectivity_policy,
        "rejected_occurrence_count": rejected_occurrence_count,
    }


__all__ = [
    "DEDUPLICATION_POLICY",
    "LineageError",
    "OccurrenceRecord",
    "SourceOccurrenceIdentity",
    "TopologyGroup",
    "build_lineage_resource",
    "group_source_occurrences",
    "lineage_summary",
    "normalized_topology_key",
    "occurrence_identity",
]
