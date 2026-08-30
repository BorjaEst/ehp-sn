"""Research-owned Dagflow generation-summary figure (Phase 5, Stage D).

This module implements ``figure:dagflow-generation-summary/v1``, a
producer-owned scientific figure in ``ehp_research`` that summarizes one
committed Dagflow ``simple-digraph/v1`` artifact release. It consumes the same
record collection the generic ``figure:simple-digraph-artifact-summary/v1``
consumes plus the committed artifact's producer-owned metadata through the
artifact-metadata surfaces (``producer-descriptors``, ``provenance``,
``auxiliary``), and reports **facts** about the configured versus observed
generation — it renders no acceptance/rejection verdict (Phase-5 · SRF-019).

Producer identity is a research-owned guard, not a framework detail
(``ARCH-001``): the figure starts by reading the committed provenance's
``specification_reference`` and raises a controlled :class:`TypeError` when it
is not ``dagflow/v1``. All producer vocabulary here is interpreted only by this
producer-owned figure.

## Selection

The gallery is ``split-edge-density-gallery`` (v1): for each canonical split
(``train``, ``validation``, ``test``) the collection is filtered by the
per-record ``split`` descriptor, ranked deterministically by edge density
(descriptor primary, stable record identity secondary), and the min/median/max
records are selected. Graph node IDs are categorical labels, never coordinates
or an order (Phase-2 § 11); graph rendering uses a circular placement, and
terminal vocabulary is used (never "goal"/"start"/"target").
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final, cast

from ehp_sn.contracts.relations import SCHEMA_REF as SIMPLE_DIGRAPH_SCHEMA_REF
from ehp_sn.contracts.relations import SimpleDigraph
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
from ehp_sn.figures.source import (
    SURFACE_AUXILIARY,
    SURFACE_PRODUCER_DESCRIPTORS,
    SURFACE_PROVENANCE,
)

from ._producer_summary_common import (
    find_auxiliary,
    guard_producer_identity,
    identity_inputs_to_dict,
    reconstruct_simple_digraph,
    record_descriptor,
    select_min_median_max,
)

#: The canonical component reference of the Dagflow generation summary.
DAGFLOW_GENERATION_SUMMARY_REF = "figure:dagflow-generation-summary/v1"

#: The expected producer specification reference for the provenance guard.
_DAGFLOW_SPEC_REF = "dagflow/v1"

#: The projection-semantics version of the generation summary.
_PROJECTION_SEMANTICS_VERSION: Final = 1

#: The preparation-semantics version of the figure.
_PREPARATION_VERSION: Final = 1

#: The visual-semantics version of the figure.
_VISUAL_SEMANTICS_VERSION: Final = 1

#: The canonical split order reported by the figure.
_CANONICAL_SPLITS: Final = ("train", "validation", "test")

#: The artifact-metadata surfaces this producer figure declares.
_METADATA_SURFACES: Final = frozenset(
    {SURFACE_PRODUCER_DESCRIPTORS, SURFACE_PROVENANCE, SURFACE_AUXILIARY}
)

#: The figure's declared metadata surface requirement.
_INPUT_REQUIREMENT = FigureInputRequirement(
    role="dagflow_generation",
    contract=SIMPLE_DIGRAPH_SCHEMA_REF,
    scope=SCOPE_ARTIFACT,
    artifact_metadata_surfaces=_METADATA_SURFACES,
)

#: Private/provisional presentation defaults (never part of projection identity).
_DEFAULT_RC_PARAMS: Final = {
    "figure.figsize": (11.0, 8.0),
    "font.size": 10,
}

#: Per-split gallery cardinality (min/median/max).
_GALLERY_CARDINALITY: Final = 3

#: National colours for the split-count facts (configured vs observed).
_CONFIGURED_COLOR: Final = "#8a9bb8"
_OBSERVED_COLOR: Final = "#2f6f9f"


@dataclass(frozen=True, slots=True)
class DagflowGenerationSummaryData:
    """Stable research-owned prepared view for ``figure:dagflow-generation-summary/v1``.

    Carries the exact committed values needed to render the summary: the
    canonical split order, the observed per-record split counts, the configured
    split counts from provenance, the authored generation configuration
    (``node_count_policy``, ``additional_edge_probability``,
    ``generation_protocol``), the compaction validation status (verbatim, when
    an auxiliary ``dagflow-validation`` resource exists), and the deterministic
    per-split representative gallery (selected identities, their split, and
    their authoritative typed ``SimpleDigraph`` views).

    This view owns no scientific computation — it is assembled by ``prepare()``
    from authoritative committed values only (Phase-5 § 38).
    """

    split_order: tuple[str, ...]
    observed_split_counts: tuple[int, ...]
    configured_split_counts: tuple[int, ...]
    node_count_policy: Any
    additional_edge_probability: Any
    generation_protocol: Any
    validation_status: Any
    selected_ids: tuple[str, ...]
    selected_splits: tuple[str, ...]
    selected_graphs: tuple[SimpleDigraph, ...]


def edge_density(node_count: int, edge_count: int) -> float:
    """Exact descriptive edge density of one ``simple-digraph/v1`` record.

    A simple directed graph has at most ``node_count * (node_count - 1)``
    directed edges (no self-loops, no duplicate edges); the **unordered** pair
    maximum used here is ``node_count * (node_count - 1) / 2``. Edge density is
    the ratio of the authoritative edge count to that maximum. The edge case
    ``node_count <= 1`` has a maximum of zero edges and is **defined** density
    ``0.0`` (Phase-4 § 22). This is an exact inspection descriptor used only for
    display/ordering/representative selection.
    """
    if node_count <= 1:
        return 0.0
    return edge_count / (node_count * (node_count - 1) / 2)


def _split_records(source: Any, split: str) -> tuple[Any, ...]:
    """Filter the collection's records whose per-record ``split`` descriptor matches."""
    return tuple(r for r in source.records if record_descriptor(r, "split") == split)


def _density_of(record: Any) -> float:
    digraph = reconstruct_simple_digraph(record.content)
    return edge_density(digraph.node_count, len(digraph.edges))


def _selected_ids_by_split(source: Any) -> dict[str, tuple[str, ...]]:
    """Deterministic per-split min/median/max representative selection.

    For each canonical split, the split's records are ranked once in ascending
    edge-density order (descriptor primary, stable record identity secondary),
    then the min/median/max records are selected. Ties resolve
    deterministically by record identity (Phase-4 · P4-ART-002).
    """
    result: dict[str, tuple[str, ...]] = {}
    for split in _CANONICAL_SPLITS:
        records = _split_records(source, split)
        candidates = [
            SelectionCandidate(record_id=r.record_id, descriptor=_density_of(r)) for r in records
        ]
        ordered = tuple(c.record_id for c in rank_candidates(candidates, order=ORDER_ASCENDING))
        result[split] = select_min_median_max(ordered)
    return result


def _select_dagflow(source: object) -> ResolvedFigureSelection:
    """``select``: resolve the split-edge-density gallery against one committed artifact."""
    content = cast(Any, source)
    guard_producer_identity(
        identity_inputs_to_dict(content.provenance),
        _DAGFLOW_SPEC_REF,
        DAGFLOW_GENERATION_SUMMARY_REF,
    )
    by_split = _selected_ids_by_split(content)
    selected: list[str] = []
    for split in _CANONICAL_SPLITS:
        selected.extend(by_split[split])
    return ResolvedFigureSelection(
        selection_ref="split-edge-density-gallery",
        selection_version=1,
        parameters={"descriptor": "edge_density", "order": "descending-with-median", "k": 3},
        resolved_identities=tuple(selected),
    )


def _prepare_dagflow(source: object) -> object:
    """``prepare``: assemble the stable :class:`DagflowGenerationSummaryData` view.

    Reads already-authoritative committed values (provenance configuration, the
    observed per-record split counts, and the deterministic per-split gallery)
    and returns the typed view in the canonical split order. It derives no
    acceptance/rejection or data-quality evidence (Phase-5 § 38).
    """
    content = cast(Any, source)
    inputs = identity_inputs_to_dict(content.provenance)
    guard_producer_identity(inputs, _DAGFLOW_SPEC_REF, DAGFLOW_GENERATION_SUMMARY_REF)

    records = content.records
    observed = tuple(
        sum(1 for r in records if record_descriptor(r, "split") == split) for split in _CANONICAL_SPLITS
    )
    configured = (
        int(inputs.get("splits_train_count") or 0),
        int(inputs.get("splits_validation_count") or 0),
        int(inputs.get("splits_test_count") or 0),
    )

    by_split = _selected_ids_by_split(content)
    by_id = {r.record_id: r for r in records}
    selected_ids: list[str] = []
    selected_splits: list[str] = []
    selected_graphs: list[SimpleDigraph] = []
    for split in _CANONICAL_SPLITS:
        for rid in by_split[split]:
            selected_ids.append(rid)
            selected_splits.append(split)
            selected_graphs.append(reconstruct_simple_digraph(by_id[rid].content))

    validation = find_auxiliary(content, "dagflow-validation")
    return DagflowGenerationSummaryData(
        split_order=_CANONICAL_SPLITS,
        observed_split_counts=observed,
        configured_split_counts=configured,
        node_count_policy=inputs.get("node_count_policy"),
        additional_edge_probability=inputs.get("additional_edge_probability"),
        generation_protocol=inputs.get("generation_protocol"),
        validation_status=validation.content if validation is not None else None,
        selected_ids=tuple(selected_ids),
        selected_splits=tuple(selected_splits),
        selected_graphs=tuple(selected_graphs),
    )


def _realize_dagflow(projection: FigureProjection) -> Any:
    """``realize``: draw split-count facts, config text, and the per-split gallery.

    Uses a 2-row layout: the first row shows the configured-versus-observed
    split counts as separate fact rows (not judged) and the authored generation
    configuration as text; the second row draws the per-split representative
    graph gallery. Terminal vocabulary is used; node IDs are categorical labels.
    """
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec

    data = cast(DagflowGenerationSummaryData, projection.content)
    figure = plt.figure()
    gs = GridSpec(2, 2, figure=figure, height_ratios=[1, 2])

    counts_ax = figure.add_subplot(gs[0, 0])
    config_ax = figure.add_subplot(gs[0, 1])
    gallery_spec = gs[1, :]

    _render_split_counts(counts_ax, data)
    _render_config(config_ax, data)
    _render_dagflow_gallery(figure, gallery_spec, data)

    figure.suptitle(
        f"Dagflow simple-digraph/v1 generation summary — {sum(data.observed_split_counts)} records",
        fontsize=12,
    )
    figure.tight_layout(rect=(0, 0, 1, 0.95))
    return figure


def _render_split_counts(ax: Any, data: DagflowGenerationSummaryData) -> None:
    """Configured versus observed split counts as separate fact rows (not judged)."""
    import numpy as np

    splits = list(data.split_order)
    x = np.arange(len(splits))
    width = 0.38
    ax.bar(
        x - width / 2,
        data.configured_split_counts,
        width,
        label="configured",
        color=_CONFIGURED_COLOR,
    )
    ax.bar(
        x + width / 2,
        data.observed_split_counts,
        width,
        label="observed",
        color=_OBSERVED_COLOR,
    )
    ax.set_xticks(x, splits)
    ax.set_ylabel("records")
    ax.set_title("split counts (configured vs observed)")
    ax.legend()
    for xi, cv, ov in zip(x, data.configured_split_counts, data.observed_split_counts, strict=True):
        ax.text(xi - width / 2, cv, str(cv), ha="center", va="bottom", fontsize=8)
        ax.text(xi + width / 2, ov, str(ov), ha="center", va="bottom", fontsize=8)


def _render_config(ax: Any, data: DagflowGenerationSummaryData) -> None:
    """Render the authored generation configuration as factual text rows."""
    ax.axis("off")
    node_policy = data.node_count_policy
    if isinstance(node_policy, (list, tuple)) and len(node_policy) == 2:
        node_text = f"{node_policy[0]} ({node_policy[1]} nodes)"
    else:
        node_text = str(node_policy)
    lines = [
        f"node_count_policy: {node_text}",
        f"additional_edge_probability: {data.additional_edge_probability}",
        f"generation_protocol: {data.generation_protocol}",
    ]
    if data.validation_status is not None:
        for key in ("single_terminal", "acyclic", "terminal_count", "all_reach"):
            value = data.validation_status.get(key) if isinstance(data.validation_status, dict) else None
            if value is not None:
                lines.append(f"{key}: {value}")
    else:
        lines.append("validation: not provided")
    ax.text(
        0.02,
        0.98,
        "\n".join(lines),
        transform=ax.transAxes,
        va="top",
        ha="left",
        family="monospace",
        fontsize=9,
    )
    ax.set_title("generation configuration")


def _render_dagflow_gallery(figure: Any, gallery_spec: Any, data: DagflowGenerationSummaryData) -> None:
    """Render the per-split representative graph gallery.

    Each canonical split is one labelled row of up to three representative
    graphs (min/median/max edge density). Graph nodes are drawn with a
    deterministic circular placement; node IDs are categorical labels, never
    coordinates (Phase-2 § 11).
    """
    nodes_per_split = len(data.split_order)
    if nodes_per_split == 0:
        return
    sub = gallery_spec.subgridspec(nodes_per_split, 2, height_ratios=[1] * nodes_per_split)

    for row, split in enumerate(data.split_order):
        label_ax = figure.add_subplot(sub[row, 0])
        label_ax.axis("off")
        label_ax.text(
            0.5,
            0.5,
            split,
            transform=label_ax.transAxes,
            ha="center",
            va="center",
            fontweight="bold",
        )
        graphs_ax = figure.add_subplot(sub[row, 1])
        graph_ids = [i for i, s in enumerate(data.selected_splits) if s == split]
        graphs_ax.set_axis_off()
        if not graph_ids:
            continue
        from matplotlib.gridspec import GridSpecFromSubplotSpec

        gs = GridSpecFromSubplotSpec(1, len(graph_ids), subplot_spec=graphs_ax.get_subplotspec())
        for col, gi in enumerate(graph_ids):
            panel = graphs_ax.figure.add_subplot(gs[col])
            _draw_graph(panel, data.selected_graphs[gi], data.selected_ids[gi])


def _draw_graph(ax: Any, graph: SimpleDigraph, record_id: str) -> None:
    """Draw one simple digraph with a deterministic circular layout.

    Node ``i`` is placed at angle ``pi/2 - 2*pi*i/node_count`` from the top,
    clockwise. Node IDs are categorical labels, never coordinates (Phase-2
    § 11); terminal vocabulary is used.
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
        ax.scatter([x], [y], s=40, c="#2f6f9f", zorder=3)
        ax.text(x, y, str(i), ha="center", va="center", color="white", fontsize=5, zorder=4)
    ax.set_axis_off()
    ax.set_title(record_id[:12], fontsize=7)
    ax.margins(0.3)


@dataclass(frozen=True, slots=True)
class DagflowGenerationSummaryFigure:
    """The ``figure:dagflow-generation-summary/v1`` reusable scientific figure."""

    ref: ComponentRef = field(default_factory=lambda: ComponentRef.parse(DAGFLOW_GENERATION_SUMMARY_REF))
    kind: str = field(default=FIGURE_KIND)
    projection: _ProjectionPartition = field(
        default_factory=lambda: _ProjectionPartition(
            semantics_version=_PROJECTION_SEMANTICS_VERSION,
            preparation_version=_PREPARATION_VERSION,
            requirement=_INPUT_REQUIREMENT,
            select=_select_dagflow,
            prepare=_prepare_dagflow,
        )
    )
    visual: _VisualPartition = field(
        default_factory=lambda: _VisualPartition(
            semantics_version=_VISUAL_SEMANTICS_VERSION,
            realize=_realize_dagflow,
        )
    )
    defaults: _DefaultsPartition = field(
        default_factory=lambda: _DefaultsPartition(rc_params=dict(_DEFAULT_RC_PARAMS))
    )


#: The canonical Dagflow generation-summary figure instance contributed by the provider.
DAGFLOW_GENERATION_SUMMARY_FIGURE: FigureSpec = DagflowGenerationSummaryFigure()


__all__ = [
    "DAGFLOW_GENERATION_SUMMARY_FIGURE",
    "DAGFLOW_GENERATION_SUMMARY_REF",
    "DagflowGenerationSummaryData",
    "edge_density",
]
