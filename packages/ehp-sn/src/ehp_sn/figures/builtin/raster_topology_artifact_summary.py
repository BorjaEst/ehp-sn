"""Framework-owned raster-topology artifact summary figure (Phase 4B).

This is the generic artifact-scope summary figure
(``figure:raster-topology-artifact-summary/v1``) introduced by Phase 4 § 25. It
operates over a committed artifact's collection of records conforming to the
framework-owned ``raster-topology/v1`` logical contract (Phase-4 § 19).

Scope and meaning:

```text
scope: artifact
role: topology
logical schema: raster-topology/v1
```

It computes exact inspection descriptors over the authoritative extent and
passability (``passable_fraction``) and reports contract-derived structure
(``state_count``, ``component_count``, ``connected``) per record (Phase-4 § 21,
§ 25; H4-3 class A/B). These support distribution panels and a deterministic
representative topology gallery; they are **not** acceptance/rejection or
data-quality evidence (Phase-4 § 21, § 34).

The figure behaves identically for every producer — DungeonGen, Maze-ND, a
producer-neutral test fixture, or a future raster producer (Phase-4 § 25, § 28).
Producer identity is irrelevant to generic compatibility (Phase-4 · H4-2).

Representative selection is deterministic and independent of incidental
candidate enumeration order (Phase-4 § 23, § 27 · P4-ART-002): the gallery is
drawn from the min/median/max ``passable_fraction`` records in the total
ascending ranking, with stable record identity as the final tie-break.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final, cast

from ehp_sn.contracts.domains import rectangular_row_column_domain
from ehp_sn.contracts.topology import SCHEMA_REF as RASTER_TOPOLOGY_SCHEMA_REF
from ehp_sn.contracts.topology import RasterTopology, raster_topology
from ehp_sn.execution import LogicalRecord
from ehp_sn.experiments import ComponentRef
from ehp_sn.figures.contracts import (
    FIGURE_KIND,
    FigureInputRequirement,
    FigureSpec,
    _DefaultsPartition,
    _ProjectionPartition,
    _VisualPartition,
)
from ehp_sn.figures.inspection import (
    ORDER_ASCENDING,
    SelectionCandidate,
    rank_candidates,
)
from ehp_sn.figures.projection import FigureProjection, ResolvedFigureSelection
from ehp_sn.figures.scope import SCOPE_ARTIFACT

#: The canonical component reference of the raster-topology artifact summary.
RASTER_TOPOLOGY_ARTIFACT_SUMMARY_REF = "figure:raster-topology-artifact-summary/v1"

#: The projection-semantics version of the artifact summary.
_PROJECTION_SEMANTICS_VERSION: Final = 1

#: The preparation-semantics version of the figure.
_PREPARATION_VERSION: Final = 1

#: The visual-semantics version of the figure.
_VISUAL_SEMANTICS_VERSION: Final = 1

#: The semantic input requirement: scope ``artifact``, role ``topology``
#: satisfied by a ``raster-topology/v1`` record collection (Phase-4 § 25).
_INPUT_REQUIREMENT = FigureInputRequirement(
    role="topology",
    contract=RASTER_TOPOLOGY_SCHEMA_REF,
    scope=SCOPE_ARTIFACT,
)

#: Private/provisional presentation defaults (never part of projection identity).
_DEFAULT_RC_PARAMS: Final = {
    "figure.figsize": (9.0, 7.0),
    "font.size": 10,
}

#: Gallery representative cardinality: one minimum-, one median-, one
#: maximum-passable-fraction topology (Phase-4 § 25).
_GALLERY_CARDINALITY: Final = 3


@dataclass(frozen=True, slots=True)
class _RasterRecordMetric:
    """Descriptors plus the authoritative typed view of one topology record."""

    record_id: str
    topology: RasterTopology
    passable_fraction: float


def _reconstruct_topology(content: object) -> RasterTopology:
    """Reconstruct the authoritative ``raster-topology/v1`` typed view.

    Reads only the contract's authoritative fields (``extent`` + ``passable``)
    and delegates to the contract's own constructor — never a producer or
    physical-storage detail (Phase-1 § 34; P4-PRE-002: 0 figure-level
    compatibility repairs for obsolete schemas).
    """
    if isinstance(content, RasterTopology):
        return content
    if not isinstance(content, dict):
        raise TypeError(
            f"raster-topology/v1 artifact summary record content must be a typed "
            f"RasterTopology or its authoritative content projection; got "
            f"{type(content).__name__}"
        )
    extent = content.get("extent")
    passable = content.get("passable")
    if not isinstance(extent, dict) or not isinstance(passable, (list, tuple)):
        raise TypeError(
            "raster-topology/v1 artifact summary record content is missing 'extent' and/or 'passable'"
        )
    try:
        height = int(extent["height"])
        width = int(extent["width"])
    except (KeyError, TypeError, ValueError) as exc:
        raise TypeError("raster-topology/v1 extent projection is missing integer height/width") from exc
    ambient = rectangular_row_column_domain(height, width)
    return raster_topology(ambient, list(passable))


def passable_fraction(topology: RasterTopology) -> float:
    """Exact passable fraction of one ``raster-topology/v1`` record.

    The fraction of positions that are passable, defined for any extent
    (``position_count >= 1`` per the ambient-domain contract), so no
    divide-by-zero edge case exists (Phase-4 § 22). This is an exact inspection
    descriptor used only for display/ordering/representative selection; it is
    not an acceptance criterion (Phase-4 § 21).
    """
    total = topology.extent.position_count
    return topology.state_count / total if total else 0.0


def _summarize(records: tuple[LogicalRecord, ...]) -> tuple[_RasterRecordMetric, ...]:
    """Compute the exact per-record descriptors and typed views (canonical order)."""
    metrics: list[_RasterRecordMetric] = []
    for record in records:
        topology = _reconstruct_topology(record.content)
        metrics.append(
            _RasterRecordMetric(
                record_id=record.record_id,
                topology=topology,
                passable_fraction=passable_fraction(topology),
            )
        )
    return tuple(metrics)


@dataclass(frozen=True, slots=True)
class RasterTopologyArtifactSummaryData:
    """Prepared summary view of a ``raster-topology/v1`` artifact collection.

    Carries the exact inspection descriptors and contract-derived structure over
    the authoritative collection, plus the deterministic representative
    topology gallery (selected record identities + their authoritative typed
    topologies).

    The exact collection identity is carried as projection provenance
    (``FigureProjection.source``), not duplicated here.
    """

    record_count: int
    record_ids: tuple[str, ...]
    extents: tuple[tuple[int, int], ...]
    state_counts: tuple[int, ...]
    passable_fractions: tuple[float, ...]
    component_counts: tuple[int, ...]
    connected_total: int
    selected_ids: tuple[str, ...]
    selected_topologies: tuple[RasterTopology, ...]


def _select_topology_representatives(
    metrics: tuple[_RasterRecordMetric, ...],
) -> tuple[str, ...]:
    """Deterministic min/median/max representative selection (Phase-4 § 25).

    Ranks the whole population once in ascending passable-fraction order
    (descriptor primary, stable record identity secondary), then selects the
    first (minimum), median, and last (maximum) records. Ties resolve
    deterministically by record identity; a small collection returns all of its
    records. Independent of incidental candidate enumeration order
    (Phase-4 · P4-ART-002).
    """
    candidates = [
        SelectionCandidate(record_id=m.record_id, descriptor=m.passable_fraction) for m in metrics
    ]
    ordered = tuple(c.record_id for c in rank_candidates(candidates, order=ORDER_ASCENDING))
    if len(ordered) <= 1:
        return ordered
    if len(ordered) == 2:
        return (ordered[0], ordered[-1])
    median_index = (len(ordered) - 1) // 2
    return (ordered[0], ordered[median_index], ordered[-1])


def _select_topology(source: object) -> ResolvedFigureSelection:
    metrics = _summarize(cast(tuple[LogicalRecord, ...], source))
    selected = _select_topology_representatives(metrics)
    return ResolvedFigureSelection(
        selection_ref="passable-fraction-gallery",
        selection_version=1,
        parameters={"k": _GALLERY_CARDINALITY, "order": "ascending", "min-median-max": True},
        resolved_identities=selected,
    )


def _prepare_topology_summary(source: object) -> object:
    """``prepare``: build the stable artifact summary view.

    Computes the exact per-record descriptors, the distribution totals, and the
    deterministic representative topology gallery. It derives no
    acceptance/data-quality evidence (Phase-4 § 21, § 34).
    """
    records = cast(tuple[LogicalRecord, ...], source)
    metrics = _summarize(records)
    # Normalize the descriptor arrays to a canonical order (by stable record
    # identity) so the prepared view is independent of the collection's
    # incidental enumeration order (Phase-4 § 27 · P4-ART-001).
    metrics = tuple(sorted(metrics, key=lambda m: m.record_id))
    selected_ids = _select_topology_representatives(metrics)
    id_to_metric = {m.record_id: m for m in metrics}
    selected_topologies = tuple(
        id_to_metric[rid].topology for rid in selected_ids if rid in id_to_metric
    )
    return RasterTopologyArtifactSummaryData(
        record_count=len(records),
        record_ids=tuple(m.record_id for m in metrics),
        extents=tuple((m.topology.extent.height, m.topology.extent.width) for m in metrics),
        state_counts=tuple(m.topology.state_count for m in metrics),
        passable_fractions=tuple(m.passable_fraction for m in metrics),
        component_counts=tuple(m.topology.component_count for m in metrics),
        connected_total=sum(1 for m in metrics if m.topology.connected),
        selected_ids=selected_ids,
        selected_topologies=selected_topologies,
    )


def _realize_topology_summary(projection: FigureProjection) -> Any:
    """``realize``: draw extent/state/fraction/component distributions + gallery.

    Uses a 2×3 Matplotlib grid: extent, state-count, passable-fraction,
    component-count distributions, a connected/disconnected total, and a
    representative topology gallery. Raster panels use the explicit scientific
    row/column mapping and passability encoding, independent of ambient
    Matplotlib state (Phase-4 § 9-11, § 25).
    """
    import matplotlib.pyplot as plt

    data = cast(RasterTopologyArtifactSummaryData, projection.content)
    figure, axes = plt.subplots(2, 3, figsize=(10.0, 7.0))

    (extent_ax, state_ax, fraction_ax) = axes[0]
    (component_ax, connected_ax, gallery_ax) = axes[1]

    extents = [h * w for (h, w) in data.extents]
    extent_ax.hist(extents, bins=min(20, max(1, len(set(extents)))), color="#2f6f9f")
    extent_ax.set_title("extent (h×w) distribution")
    extent_ax.set_xlabel("positions")
    extent_ax.set_ylabel("records")

    state_ax.hist(data.state_counts, bins=min(20, max(1, len(set(data.state_counts)))), color="#2f6f9f")
    state_ax.set_title("state_count distribution")
    state_ax.set_xlabel("passable positions")
    state_ax.set_ylabel("records")

    fraction_ax.hist(data.passable_fractions, bins=16, color="#2f6f4f")
    fraction_ax.set_title("passable_fraction distribution")
    fraction_ax.set_xlabel("passable_fraction")
    fraction_ax.set_ylabel("records")

    component_ax.hist(
        data.component_counts,
        bins=min(20, max(1, len(set(data.component_counts)))),
        color="#6f6f9f",
    )
    component_ax.set_title("component_count distribution")
    component_ax.set_xlabel("connectivity components")
    component_ax.set_ylabel("records")

    connected_ax.bar(
        ["connected", "disconnected"],
        [data.connected_total, data.record_count - data.connected_total],
        color=["#2f6f4f", "#6f4f4f"],
    )
    connected_ax.set_title("connected/disconnected")
    connected_ax.set_ylabel("records")

    _draw_topology_gallery(gallery_ax, data)
    figure.suptitle(
        f"raster-topology/v1 artifact summary — {data.record_count} records",
        fontsize=12,
    )
    figure.tight_layout(rect=(0, 0, 1, 0.94))
    return figure


def _draw_topology_gallery(gallery_ax: Any, data: RasterTopologyArtifactSummaryData) -> None:
    """Draw up to three selected topologies side by side on the gallery sub-axes.

    Each raster uses the explicit scientific row/column mapping (via
    :func:`ehp_sn.figures.rectangular_realization.to_matrix`), explicit
    ``origin="upper"`` and ``interpolation="nearest"``, and a passable/blocked
    encoding independent of ambient Matplotlib state (Phase-4 § 9-11).
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap

    from ehp_sn.figures.rectangular_realization import to_matrix

    gallery_ax.set_axis_off()
    gallery_ax.set_title("representative topologies (min/median/max fraction)")
    count = len(data.selected_topologies)
    if count == 0:
        return
    from matplotlib.gridspec import GridSpecFromSubplotSpec

    gs = GridSpecFromSubplotSpec(1, count, subplot_spec=gallery_ax.get_subplotspec())
    cmap = ListedColormap(["#d8d8d8", "#2f6f4f"])
    for i, topology in enumerate(data.selected_topologies):
        sub = gallery_ax.figure.add_subplot(gs[i])
        grid = to_matrix(topology.extent, [1 if p else 0 for p in topology.passable])
        sub.imshow(
            grid,
            cmap=cmap,
            interpolation="nearest",
            aspect="equal",
            origin="upper",
        )
        sub.set_axis_off()
    _ = plt


@dataclass(frozen=True, slots=True)
class RasterTopologyArtifactSummaryFigure:
    """The Phase-4 ``figure:raster-topology-artifact-summary/v1`` executable figure."""

    ref: ComponentRef = field(
        default_factory=lambda: ComponentRef.parse(RASTER_TOPOLOGY_ARTIFACT_SUMMARY_REF)
    )
    kind: str = field(default=FIGURE_KIND)
    projection: _ProjectionPartition = field(
        default_factory=lambda: _ProjectionPartition(
            semantics_version=_PROJECTION_SEMANTICS_VERSION,
            preparation_version=_PREPARATION_VERSION,
            requirement=_INPUT_REQUIREMENT,
            select=_select_topology,
            prepare=_prepare_topology_summary,
        )
    )
    visual: _VisualPartition = field(
        default_factory=lambda: _VisualPartition(
            semantics_version=_VISUAL_SEMANTICS_VERSION,
            realize=_realize_topology_summary,
        )
    )
    defaults: _DefaultsPartition = field(
        default_factory=lambda: _DefaultsPartition(rc_params=dict(_DEFAULT_RC_PARAMS))
    )


#: The canonical framework-owned raster-topology artifact summary figure instance.
RASTER_TOPOLOGY_ARTIFACT_SUMMARY_FIGURE: FigureSpec = RasterTopologyArtifactSummaryFigure()


__all__ = [
    "RASTER_TOPOLOGY_ARTIFACT_SUMMARY_FIGURE",
    "RASTER_TOPOLOGY_ARTIFACT_SUMMARY_REF",
    "RasterTopologyArtifactSummaryData",
]
