"""Framework-owned simple-digraph artifact summary figure (Phase 4B).

This is the generic artifact-scope summary figure
(``figure:simple-digraph-artifact-summary/v1``) introduced by Phase 4 § 24. It
operates over a committed artifact's collection of records conforming to the
framework-owned ``simple-digraph/v1`` logical contract (Phase-4 § 19).

Scope and meaning:

```text
scope: artifact
role: graph
logical schema: simple-digraph/v1
```

It computes **exact inspection descriptors** over the authoritative edge
relation (``edge_count``, ``edge_density``) and reports contract-derived
structure (``acyclic``, ``all_nodes_reach_a_terminal``) per record (Phase-4
§ 21, § 24; H4-3 class A/B). These descriptors support population-structure
guides and a deterministic representative gallery; they are **not** acceptance,
rejection, or data-quality evidence (Phase-4 § 21, § 34: figures establish no
substrate acceptance/data-quality claims).

The representative gallery (min/median/max edge density) is selected by
:func:`ehp_sn.figures.inspection.select_representatives`, which is deterministic
and independent of incidental candidate enumeration order; stable record
identity is the final tie-break (Phase-4 § 23, § 27 · P4-ART-002).

The figure is producer-independent (Phase-4 § 28): Dagflow and a producer-neutral
fixture declaring a different family but records conforming to
``simple-digraph/v1`` travel the exact same generic path and require no semantic
modification here (Phase-4 · P4-ARCH-001).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final, cast

from ehp_sn.contracts.relations import SCHEMA_REF as SIMPLE_DIGRAPH_SCHEMA_REF
from ehp_sn.contracts.relations import SimpleDigraph, simple_digraph
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

#: The canonical component reference of the simple-digraph artifact summary.
SIMPLE_DIGRAPH_ARTIFACT_SUMMARY_REF = "figure:simple-digraph-artifact-summary/v1"

#: The projection-semantics version of the artifact summary.
_PROJECTION_SEMANTICS_VERSION: Final = 1

#: The preparation-semantics version of the figure.
_PREPARATION_VERSION: Final = 1

#: The visual-semantics version of the figure.
_VISUAL_SEMANTICS_VERSION: Final = 1

#: The semantic input requirement: scope ``artifact``, role ``graph`` satisfied
#: by a ``simple-digraph/v1`` record collection (Phase-4 § 24).
_INPUT_REQUIREMENT = FigureInputRequirement(
    role="graph",
    contract=SIMPLE_DIGRAPH_SCHEMA_REF,
    scope=SCOPE_ARTIFACT,
)

#: Private/provisional presentation defaults (never part of projection identity).
_DEFAULT_RC_PARAMS: Final = {
    "figure.figsize": (8.0, 6.0),
    "font.size": 10,
}

#: Gallery representative cardinality: one minimum-, one median-, one
#: maximum-edge-density record (Phase-4 § 24).
_GALLERY_CARDINALITY: Final = 3


@dataclass(frozen=True, slots=True)
class _DigraphRecordMetric:
    """Descriptors plus the authoritative typed view of one graph record."""

    record_id: str
    digraph: SimpleDigraph
    edge_count: int
    edge_density: float


def _reconstruct_digraph(content: object) -> SimpleDigraph:
    """Reconstruct the authoritative ``simple-digraph/v1`` typed view.

    Reads only the contract's authoritative fields (``node_count`` + ``edges``)
    and delegates to the contract's own constructor — never a producer or
    physical-storage detail, and never a reimplementation of derived properties
    (Phase-2 § 5; Phase-1 § 34).
    """
    if isinstance(content, SimpleDigraph):
        return content
    if not isinstance(content, dict):
        raise TypeError(
            f"simple-digraph/v1 artifact summary record content must be a typed "
            f"SimpleDigraph or its authoritative content projection; got "
            f"{type(content).__name__}"
        )
    raw_count = content.get("node_count")
    raw_edges = content.get("edges")
    if not isinstance(raw_count, int) or not isinstance(raw_edges, (list, tuple)):
        raise TypeError(
            "simple-digraph/v1 artifact summary record content is missing integer "
            "'node_count' and/or 'edges'"
        )
    return simple_digraph(
        int(raw_count),
        tuple((int(s), int(t)) for s, t in raw_edges),  # type: ignore[misc]
    )


def edge_density(digraph: SimpleDigraph) -> float:
    """Exact descriptive edge density of one ``simple-digraph/v1`` record.

    A simple directed graph has at most ``node_count * (node_count - 1)``
    directed edges (no self-loops, no duplicate edges). Edge density is the
    ratio of the authoritative edge count to that maximum. The edge case
    ``node_count == 1`` has a maximum of zero edges and is **defined** density
    ``0.0`` rather than relying on a divide-by-zero (Phase-4 § 22). This is an
    exact inspection descriptor used only for display/ordering/representative
    selection; it is not an acceptance criterion (Phase-4 § 21).
    """
    n = digraph.node_count
    if n <= 1:
        return 0.0
    max_edges = n * (n - 1)
    return len(digraph.edges) / max_edges


def _summarize(records: tuple[LogicalRecord, ...]) -> tuple[_DigraphRecordMetric, ...]:
    """Compute the exact per-record descriptors and typed views (canonical order).

    Iterates the collection in its stable order and reconstructs each record's
    authoritative typed ``SimpleDigraph`` plus its exact descriptors. A record
    whose content is not a conforming authoritative ``simple-digraph/v1``
    projection raises a controlled ``TypeError`` — an artifact-scope summary
    requires a conforming collection (Phase-4 § 20).
    """
    metrics: list[_DigraphRecordMetric] = []
    for record in records:
        digraph = _reconstruct_digraph(record.content)
        metrics.append(
            _DigraphRecordMetric(
                record_id=record.record_id,
                digraph=digraph,
                edge_count=len(digraph.edges),
                edge_density=edge_density(digraph),
            )
        )
    return tuple(metrics)


@dataclass(frozen=True, slots=True)
class SimpleDigraphArtifactSummaryData:
    """Prepared summary view of a ``simple-digraph/v1`` artifact collection.

    Carries the exact inspection descriptors and contract-derived structure over
    the authoritative collection, plus the deterministic representative gallery
    (selected record identities and their authoritative typed graphs).

    The exact collection identity is carried as projection provenance
    (``FigureProjection.source``), not duplicated here.
    """

    record_count: int
    record_ids: tuple[str, ...]
    edge_counts: tuple[int, ...]
    edge_densities: tuple[float, ...]
    terminal_counts: tuple[int, ...]
    acyclic_flag_total: int
    all_reach_terminal_total: int
    selected_ids: tuple[str, ...]
    selected_graphs: tuple[SimpleDigraph, ...]


def _select_graph_representatives(
    metrics: tuple[_DigraphRecordMetric, ...],
) -> tuple[str, ...]:
    """Deterministic min/median/max representative selection (Phase-4 § 24).

    Ranks the whole population once in ascending edge-density order (descriptor
    primary, stable record identity secondary), then selects the first
    (minimum-density), median, and last (maximum-density) records. Ties resolve
    deterministically by record identity; a collection with fewer than three
    records returns all of them, still in the total deterministic order. The
    result is independent of incidental candidate enumeration order
    (Phase-4 · P4-ART-002).
    """
    candidates = [SelectionCandidate(record_id=m.record_id, descriptor=m.edge_density) for m in metrics]
    ordered = tuple(c.record_id for c in rank_candidates(candidates, order=ORDER_ASCENDING))
    if len(ordered) <= 1:
        return ordered
    if len(ordered) == 2:
        return (ordered[0], ordered[-1])
    median_index = (len(ordered) - 1) // 2
    return (ordered[0], ordered[median_index], ordered[-1])


def _select_graph(source: object) -> ResolvedFigureSelection:
    metrics = _summarize(cast(tuple[LogicalRecord, ...], source))
    selected = _select_graph_representatives(metrics)
    return ResolvedFigureSelection(
        selection_ref="edge-density-gallery",
        selection_version=1,
        parameters={"k": _GALLERY_CARDINALITY, "order": "ascending", "min-median-max": True},
        resolved_identities=selected,
    )


def _prepare_graph_summary(source: object) -> object:
    """``prepare``: build the stable artifact summary view.

    Computes the exact per-record descriptors, the population-structure totals,
    and the deterministic representative gallery (selected identities + their
    authoritative graphs). It derives no acceptance/data-quality evidence; every
    descriptor is an exact inspection descriptor over authoritative content
    (Phase-4 § 21, § 34).
    """
    records = cast(tuple[LogicalRecord, ...], source)
    metrics = _summarize(records)
    # Normalize the descriptor arrays to a canonical order (by stable record
    # identity) so the prepared view is independent of the collection's
    # incidental enumeration order (Phase-4 § 27 · P4-ART-001).
    metrics = tuple(sorted(metrics, key=lambda m: m.record_id))
    selected_ids = _select_graph_representatives(metrics)
    id_to_metric = {m.record_id: m for m in metrics}
    selected_graphs = tuple(id_to_metric[rid].digraph for rid in selected_ids if rid in id_to_metric)
    return SimpleDigraphArtifactSummaryData(
        record_count=len(records),
        record_ids=tuple(m.record_id for m in metrics),
        edge_counts=tuple(m.edge_count for m in metrics),
        edge_densities=tuple(m.edge_density for m in metrics),
        terminal_counts=tuple(m.digraph.terminal_count for m in metrics),
        acyclic_flag_total=sum(1 for m in metrics if m.digraph.acyclic),
        all_reach_terminal_total=sum(1 for m in metrics if m.digraph.all_nodes_reach_a_terminal),
        selected_ids=selected_ids,
        selected_graphs=selected_graphs,
    )


def _realize_graph_summary(projection: FigureProjection) -> Any:
    """``realize``: draw the artifact summary (distributions + representative gallery).

    Uses a 2×2 Matplotlib grid: edge-count and terminal-count distributions, a
    contract-derived structure panel (acyclic / all-nodes-reach-a-terminal
    totals), and a representative gallery of up to three selected graphs drawn
    with the deterministic circular placement. No producer vocabulary and no
    acceptance threshold is drawn (Phase-4 § 21-24).
    """
    import matplotlib.pyplot as plt

    data = cast(SimpleDigraphArtifactSummaryData, projection.content)
    figure, axes = plt.subplots(2, 2, figsize=(9.0, 7.0))

    edge_ax, terminal_ax, structure_ax, gallery_ax = axes.ravel()

    edge_ax.hist(
        data.edge_counts,
        bins=min(20, max(1, len(set(data.edge_counts)))),
        color="#2f6f9f",
    )
    edge_ax.set_title("edge_count distribution (inspection descriptor)")
    edge_ax.set_xlabel("edge_count")
    edge_ax.set_ylabel("records")

    terminal_ax.hist(
        data.terminal_counts,
        bins=min(8, max(1, len(set(data.terminal_counts)))),
        color="#2f6f4f",
    )
    terminal_ax.set_title("terminal_count distribution")
    terminal_ax.set_xlabel("terminal_count")
    terminal_ax.set_ylabel("records")

    structure_ax.bar(
        ["acyclic", "all reach terminal"],
        [data.acyclic_flag_total, data.all_reach_terminal_total],
        color=["#2f6f9f", "#2f6f4f"],
    )
    structure_ax.set_title("contract-derived structure (per-record counts)")
    structure_ax.set_ylabel("records")

    _draw_graph_gallery(gallery_ax, data)
    figure.suptitle(
        f"simple-digraph/v1 artifact summary — {data.record_count} records",
        fontsize=12,
    )
    figure.tight_layout(rect=(0, 0, 1, 0.94))
    return figure


def _draw_graph_gallery(gallery_ax: Any, data: SimpleDigraphArtifactSummaryData) -> None:
    """Draw up to three selected graphs side by side on the gallery sub-axes.

    Deterministic circular placement is reused for each panel. Node IDs are
    categorical labels, never coordinates (Phase-2 § 11). The gallery shows the
    min/median/max edge-density representatives; no acceptance semantics are
    introduced (Phase-4 § 21, § 24).
    """
    import matplotlib.pyplot as plt

    gallery_ax.set_axis_off()
    gallery_ax.set_title("representative graphs (min/median/max density)")
    count = len(data.selected_graphs)
    if count == 0:
        return
    from matplotlib.gridspec import GridSpecFromSubplotSpec

    gs = GridSpecFromSubplotSpec(1, count, subplot_spec=gallery_ax.get_subplotspec())
    for i, graph in enumerate(data.selected_graphs):
        sub = gallery_ax.figure.add_subplot(gs[i])
        _draw_single_graph_on_axes(sub, graph)
    _ = plt


def _draw_single_graph_on_axes(ax: Any, graph: SimpleDigraph) -> None:
    """Draw one simple digraph on a sub-axes with deterministic circular layout.

    Reuses deterministic circular placement: node ``i`` at angle
    ``2*pi*i/node_count`` from the top, clockwise. Node IDs are categorical
    labels, never coordinates (Phase-2 § 11). No producer vocabulary and no
    acceptance semantics are introduced (Phase-4 § 21).
    """
    import math

    node_count = graph.node_count
    positions: dict[int, tuple[float, float]] = {}
    for i in range(node_count):
        angle = math.pi / 2 - 2.0 * math.pi * i / max(node_count, 1)
        positions[i] = (math.cos(angle), math.sin(angle))
    ax.set_aspect("equal")
    for source, target in graph.edges:
        x0, y0 = positions[source]
        x1, y1 = positions[target]
        ax.annotate(
            "",
            xy=(x1, y1),
            xytext=(x0, y0),
            arrowprops=dict(arrowstyle="->", color="#555555", lw=1.0),
        )
    for i, (x, y) in positions.items():
        ax.scatter([x], [y], s=60, c="#2f6f9f", zorder=3)
        ax.text(x, y, str(i), ha="center", va="center", color="white", fontsize=6, zorder=4)
    ax.set_axis_off()
    ax.margins(0.3)


@dataclass(frozen=True, slots=True)
class SimpleDigraphArtifactSummaryFigure:
    """The Phase-4 ``figure:simple-digraph-artifact-summary/v1`` executable figure."""

    ref: ComponentRef = field(
        default_factory=lambda: ComponentRef.parse(SIMPLE_DIGRAPH_ARTIFACT_SUMMARY_REF)
    )
    kind: str = field(default=FIGURE_KIND)
    projection: _ProjectionPartition = field(
        default_factory=lambda: _ProjectionPartition(
            semantics_version=_PROJECTION_SEMANTICS_VERSION,
            preparation_version=_PREPARATION_VERSION,
            requirement=_INPUT_REQUIREMENT,
            select=_select_graph,
            prepare=_prepare_graph_summary,
        )
    )
    visual: _VisualPartition = field(
        default_factory=lambda: _VisualPartition(
            semantics_version=_VISUAL_SEMANTICS_VERSION,
            realize=_realize_graph_summary,
        )
    )
    defaults: _DefaultsPartition = field(
        default_factory=lambda: _DefaultsPartition(rc_params=dict(_DEFAULT_RC_PARAMS))
    )


#: The canonical framework-owned simple-digraph artifact summary figure instance.
SIMPLE_DIGRAPH_ARTIFACT_SUMMARY_FIGURE: FigureSpec = SimpleDigraphArtifactSummaryFigure()


__all__ = [
    "SIMPLE_DIGRAPH_ARTIFACT_SUMMARY_FIGURE",
    "SIMPLE_DIGRAPH_ARTIFACT_SUMMARY_REF",
    "SimpleDigraphArtifactSummaryData",
]
