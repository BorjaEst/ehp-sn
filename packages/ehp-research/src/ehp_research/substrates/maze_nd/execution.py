"""Maze-ND execution operation (producer integration).

This module owns the *producer execution operation* for the registered
``substrate:maze-nd/v1`` definition: the research-side callable bound to the
definition through the framework execution composition.

It consumes the authoritative, opaque producer-effective configuration and the
exact bound source resource from the framework-owned
:class:`~ehp_sn.execution.MaterializationSession`, loads and verifies the
immutable source, extracts and normalizes every selected source row, applies
the connectivity policy, deduplicates to unique normalized topologies, groups
complete source lineage, and materializes each unique topology through the
framework's ``GeneratedRecordBody`` boundary. The framework derives the
``record_id``; Maze-ND never creates ``record_id``, ``ArtifactRef``, a release
coordinate, a manifest, or a final filesystem path itself.

The only shared topology constructor is ``raster-topology/v1``:
Maze-ND delegates ``state_id``, state/position maps, ``next_state``,
``movement_valid``, ``component_count``, ``connected``, and grid4 ordering to
``ehp_sn.contracts.topology.raster_topology`` and never re-enumerates them.
"""

from __future__ import annotations

from ehp_sn.contracts.domains import RectangularRowColumnDomain
from ehp_sn.contracts.topology import raster_topology
from ehp_sn.execution import (
    GeneratedRecordBody,
    MaterializationSession,
    RealizationKey,
)
from ehp_sn.planning import IdentityInput, ResolvedResource

from .configuration import MazeNDConfiguration
from .extraction import ExtractedTopology
from .lineage import (
    build_lineage_resource,
    group_source_occurrences,
    occurrence_identity,
)
from .normalization import normalize
from .source import load_source

#: The canonical requirement reference of the Maze-ND upstream source bound by
#: planning (must match planning.py).
_SOURCE_REQUIREMENT_REF = "requirement:substrate/maze-nd-source/v1"


class MazeNDExecutionError(ValueError):
    """A controlled Maze-ND producer execution failure.

    Raised for an invalid session configuration, an absent/ambiguous bound
    source resource, or any Maze-ND import failure. Translated by the generic
    build boundary into a controlled build error; the CLI maps it at its own
    layer.
    """


def _bound_source(session: MaterializationSession) -> ResolvedResource:
    """Return the exact source resource bound into the plan.

    The producer must receive exactly the source bound into the plan:
    exactly one ``raw-source`` requirement resource is expected. A missing or
    ambiguous resource is a controlled failure rather than an ad hoc selection.
    """
    candidates = [
        resource for resource in session.resources if resource.requirement_ref == _SOURCE_REQUIREMENT_REF
    ]
    if len(candidates) != 1:
        raise MazeNDExecutionError(
            f"expected exactly one bound source resource for requirement "
            f"{_SOURCE_REQUIREMENT_REF!r}, found {len(candidates)}"
        )
    return candidates[0]


def _realization_key(
    configuration: MazeNDConfiguration,
    height: int,
    width: int,
    passable: tuple[bool, ...],
) -> RealizationKey:
    """Declare the producer-owned canonical realization identity for one topology.

    The identity is derived from the normalized topology content (extent +
    preserved-orientation passability) and the resolved scientific source
    semantics. It deliberately does **not** depend on the first-encountered
    duplicate source row, source iteration order, payload filename, or worker
    assignment: equal normalized topology + equal scientific semantics always
    yield the same realization key.
    """
    return RealizationKey(
        inputs=(
            IdentityInput("specification_reference", "maze-nd/v1"),
            IdentityInput("variant", configuration.variant),
            IdentityInput("source_revision", configuration.source_revision),
            IdentityInput("source_fingerprint", configuration.source_fingerprint),
            IdentityInput("extraction_schema", configuration.source_schema),
            IdentityInput("normalization_policy", configuration.normalization_policy),
            IdentityInput("connectivity_policy", configuration.connectivity_policy),
            IdentityInput("deduplication_policy", configuration.deduplication_policy),
            IdentityInput("extent", (height, width)),
            IdentityInput("passable", list(passable)),
        )
    )


def _planned_rows(
    configuration: MazeNDConfiguration,
    resource_source: str,
) -> list[ExtractedTopology]:
    """Load and validate every selected source row in canonical source order.

    The real path calls ``load_source``: fetch the exact bound immutable
    revision, verify the content fingerprint, and parse all rows. Tests
    monkeypatch ``ehp_research.substrates.maze_nd.source.load_source`` with a
    fixture loader to avoid network access while exercising the identical
    downstream pipeline.
    """
    return list(load_source(configuration, resource_source))


def _unique_topologies(
    configuration: MazeNDConfiguration,
    rows: list[ExtractedTopology],
):
    """Run extraction→normalize→connectivity→selection/dedup→lineage grouping.

    Returns ``(groups, rejected)`` where ``groups`` are unique normalized
    topology groups (dedup) and ``rejected`` is the count of source rows rejected
    by an explicit connectivity ``reject`` policy (never silently repaired).
    """
    normalized = []
    rejected = 0
    for extracted in rows:
        height, width, passable = normalize(extracted)
        # Connectivity policy applied per normalized topology, before dedup.
        if configuration.connectivity_policy == "reject":
            topology = raster_topology(RectangularRowColumnDomain(height, width), passable)
            if topology.component_count != 1:
                rejected += 1
                continue
        identity = occurrence_identity(extracted, source_revision=configuration.source_revision)
        normalized.append((height, width, passable, identity, extracted.source_metadata))

    groups = group_source_occurrences(normalized)
    return groups, rejected


def execute(session: MaterializationSession) -> None:
    """Execute the Maze-ND producer operation against the framework session.

    Reads the opaque :class:`MazeNDConfiguration` and the exact bound source
    resource from the authoritative session, loads and verifies the immutable
    source, runs extraction/normalization/dedup/lineage, and materializes each
    unique normalized topology plus the complete source-lineage resource.

    The producer never performs framework-owned lifecycle work; it supplies
    realization-identity inputs and bounded lineage descriptors and lets the
    framework derive ``record_id``.
    """
    configuration = session.configuration
    if not isinstance(configuration, MazeNDConfiguration):
        raise MazeNDExecutionError(f"expected MazeNDConfiguration, got {type(configuration).__name__}")

    resource = _bound_source(session)
    rows = _planned_rows(configuration, resource.resource_ref)
    groups, rejected = _unique_topologies(configuration, rows)

    # Build the shared RasterTopology for each unique normalized topology exactly
    # once, using the raster-topology/v1 constructor.
    record_ids: dict[tuple[int, int, tuple[bool, ...]], str] = {}
    for group in groups:
        topology = raster_topology(RectangularRowColumnDomain(group.height, group.width), group.passable)
        key = (group.height, group.width, group.passable)
        descriptors = (
            IdentityInput("source_occurrence_count", group.occurrence_count),
            IdentityInput("source_split_labels", tuple(group.source_split_labels)),
            IdentityInput("lineage_resource", "source-lineage"),
        )
        record = session.add_record(
            GeneratedRecordBody(
                content=topology.content(),
                realization_key=_realization_key(
                    configuration, group.height, group.width, group.passable
                ),
                descriptors=descriptors,
            )
        )
        record_ids[key] = record.record_id

    # Complete many-to-one lineage in a separate logical resource.
    session.add_logical_resource(
        "source-lineage",
        build_lineage_resource(
            groups,
            source_revision=configuration.source_revision,
            record_ids=record_ids,
            connectivity_policy=configuration.connectivity_policy,
            rejected_occurrence_count=rejected,
        ),
        resource_kind="lineage",
    )


__all__ = ["MazeNDExecutionError", "execute"]
