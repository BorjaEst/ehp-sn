"""Research-owned HPC place-summary figure (Phase 3).

This module implements ``figure:hpc-place-summary/v1``, the first full
reusable scientific figure owned by ``ehp_research``. It reuses the generic
figure service and ``FigureProjection`` boundary unchanged while keeping all
HPC scientific meaning downstream in ``ehp_research`` (P3-T1 · G2).

The figure consumes one stable authoritative :class:`~ehp_research.analysis
.HpcAnalysis` source bound to role ``hpc_analysis`` (contract ``hpc-analysis/v1``),
resolves a deterministic research-owned selection
(:class:`~ehp_research.figures.selection.TopSpatialInformationCells`), prepares a
typed :class:`HpcPlaceSummaryData` view, and realizes the projection through a
research-owned scientific visual coordinator with three semantic panels:

```text
population   — population distribution of spatial selectivity (primary)
coverage     — spatial distribution of authoritative field centres (secondary)
examples     — cells selected by the declared highest-SI policy (detail)
```

The ``examples`` panel is explicitly **highest-SI exemplars**, not a
representative population sample (P3-T9 · G11): the top-eight selection is
deliberately biased toward high spatial information.

## Value-to-visual semantics (P3-T11)

The declared scientific interpretation is **cell-local normalization**: the
goal is to compare the spatial field *shape* within each cell, not absolute
activity magnitude across cells. Each example rate map is therefore normalized
to its own local value domain (0 .. its own max) with a shared colormap whose
meaning is "relative firing within one cell's field". This mapping is explicit
and versioned (``visual_semantics_version = 1``).

## Panel != Axes (P3-T14)

The examples semantic panel maps to one top-level structural region and is
realized through a nested ``subgridspec(2, 4)`` giving 8 Matplotlib Axes. The
complete figure therefore has one Figure, and more than three Axes (population:
1, coverage: 1, examples: 8) — proving that a semantic panel is not one Axes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final, cast

from ehp_sn.experiments import ComponentRef
from ehp_sn.figures import FigureProjection, ResolvedFigureSelection
from ehp_sn.figures.contracts import (
    FIGURE_KIND,
    FigureInputRequirement,
    FigureSpec,
    _DefaultsPartition,
    _ProjectionPartition,
    _VisualPartition,
)

from ehp_research.analysis import HpcAnalysis
from ehp_research.figures.selection import (
    TopSpatialInformationCells,
    resolve_top_spatial_information,
)

#: The canonical component reference of the HPC place-summary figure.
HPC_PLACE_SUMMARY_REF = "figure:hpc-place-summary/v1"

#: The logical contract the authoritative source must satisfy for role
#: ``hpc_analysis``.
HPC_ANALYSIS_CONTRACT = "hpc-analysis/v1"

#: Projection-semantics version of ``figure:hpc-place-summary/v1``.
_PROJECTION_SEMANTICS_VERSION: Final = 1
#: Preparation-semantics version (how ``prepare`` interprets the source).
_PREPARATION_VERSION: Final = 1
#: Visual-semantics version (scientific graphical meaning; includes the
#: per-cell-normalization value-to-visual mapping decision).
_VISUAL_SEMANTICS_VERSION: Final = 1

#: The authored selection applied by this figure: top 8 valid cells by
#: spatial information. Both ``select`` and ``prepare`` reference this one
#: declared selection so they never diverge.
_AUTHORED_SELECTION = TopSpatialInformationCells(count=8)

_INPUT_REQUIREMENT = FigureInputRequirement(
    role="hpc_analysis",
    contract=HPC_ANALYSIS_CONTRACT,
)

#: Private/provisional presentation defaults (never part of projection identity).
_DEFAULT_RC_PARAMS: Final = {
    "figure.figsize": (12.0, 8.0),
    "font.size": 10,
}

#: Per-cell normalization colormap (shared across all example rate maps).
_EXAMPLE_CMAP: Final = "viridis"
#: Field-centre marker colour (coverage panel).
_FIELD_CENTRE_COLOR: Final = "#c0392b"


# ---------------------------------------------------------------------------
# Typed research-owned prepared view (P3-T7 / G8)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class HpcPlaceSummaryData:
    """Stable research-owned prepared view for ``figure:hpc-place-summary/v1``.

    Carries exactly the already-authoritative values needed to render the three
    semantic panels, in the exact resolved selection order:

    ``selected_cell_ids``, ``selected_spatial_information``,
    ``selected_rate_maps`` (flat rows of ``domain.height*width``) and
    ``selected_field_centres`` follow the resolved selection order;
    ``population_spatial_information`` is the finite-SI distribution across the
    whole valid population; ``domain`` carries the authoritative spatial-domain
    semantics for rendering.

    This view owns no scientific computation — it is assembled by ``prepare()``
    from authoritative values only (P3-T6 · G7). It is immutable.
    """

    selected_cell_ids: tuple[str, ...]
    selected_spatial_information: tuple[float, ...]
    selected_rate_maps: tuple[tuple[float, ...], ...]
    selected_field_centres: tuple[tuple[int, int], ...]
    population_spatial_information: tuple[float, ...]
    domain: Any


# ---------------------------------------------------------------------------
# Semantic panel registry and validated region binding (P3-T9 · P3-T13)
# ---------------------------------------------------------------------------

#: The three stable top-level scientific/communication objectives.
_SEMANTIC_PANELS: Final = ("population", "coverage", "examples")

#: Required structural regions (generic placement names, not meaning).
_REQUIRED_REGIONS: Final = ("primary", "secondary", "detail")

#: Strict semantic-panel → structural-region binding for this figure.
_PANEL_TO_REGION: Final = {
    "population": "primary",
    "coverage": "secondary",
    "examples": "detail",
}


class LayoutBindingError(ValueError):
    """A controlled failure when the semantic-panel ↔ region binding is invalid."""


def _validate_panel_region_binding(
    panel_to_region: dict[str, str],
    panels: tuple[str, ...],
    regions: tuple[str, ...],
) -> dict[str, str]:
    """Validate the strict (bijective) semantic-panel ↔ region binding (P3-T13).

    Requires one authoritative mapping with no unknown, duplicate, or missing
    panel or region keys for the required sets. This is a research-local
    validated mapping sufficient for the Phase-3 figure; it does not stabilize a
    public framework layout API (``P3-T12``/``P3-T15``).
    """
    mapping = dict(panel_to_region)
    if set(mapping) != set(panels):
        raise LayoutBindingError(f"panel keys must be exactly {set(panels)}, got {set(mapping)}")
    if set(mapping.values()) != set(regions):
        raise LayoutBindingError(
            f"region keys must be exactly {set(regions)}, got {set(mapping.values())}"
        )
    return mapping


# ---------------------------------------------------------------------------
# Selection resolver (P3-T4 · P3-T5) and preparation (P3-T6)
# ---------------------------------------------------------------------------


def _select_hpc_cells(source: object) -> ResolvedFigureSelection:
    """``select``: resolve the declared selection against one authoritative analysis.

    The authoritative source content is an :class:`HpcAnalysis`. The resolved
    selection carries the authored semantics (identity/version + parameters) and
    the exact resolved cell identities (P3-T5).
    """
    analysis = _as_hpc_analysis(source)
    return _AUTHORED_SELECTION.resolve(analysis)


def _as_hpc_analysis(source: object) -> HpcAnalysis:
    """Coerce the authoritative source content to an :class:`HpcAnalysis`."""
    if isinstance(source, HpcAnalysis):
        return source
    raise TypeError(
        f"figure:hpc-place-summary/v1 source must be an authoritative HpcAnalysis; "
        f"got {type(source).__name__}"
    )


def _prepare_hpc_place_summary(source: object) -> object:
    """``prepare``: assemble a stable :class:`HpcPlaceSummaryData` view.

    Reads already-authoritative values (cell identity, spatial information, rate
    maps, field centres, population distribution, spatial domain), applies the
    same declared selection deterministically for ordering, and returns the
    typed view. It creates no new independently scientifically interpretable
    quantity (P3-T6 · G7 · FIG-002): it never estimates a rate map, computes
    spatial information, or calculates a field centre.
    """
    analysis = _as_hpc_analysis(source)
    resolved = resolve_top_spatial_information(analysis, _AUTHORED_SELECTION.count)
    selected_ids = tuple(str(x) for x in resolved.resolved_identities)
    by_id = {cell.cell_id: cell for cell in analysis.cells}

    selected_si: list[float] = []
    selected_maps: list[tuple[float, ...]] = []
    selected_centres: list[tuple[int, int]] = []
    for cell_id in selected_ids:
        cell = by_id[cell_id]
        selected_si.append(cell.spatial_information)
        selected_maps.append(cell.rate_map)
        selected_centres.append(cell.field_centre)

    return HpcPlaceSummaryData(
        selected_cell_ids=selected_ids,
        selected_spatial_information=tuple(selected_si),
        selected_rate_maps=tuple(selected_maps),
        selected_field_centres=tuple(selected_centres),
        population_spatial_information=tuple(
            cell.spatial_information for cell in analysis.valid_cells()
        ),
        domain=analysis.domain,
    )


# ---------------------------------------------------------------------------
# Scientific visual coordinator (P3-T10 · P3-T12 · P3-T14 · P3-T16)
# ---------------------------------------------------------------------------


def _realize_hpc_place_summary(projection: FigureProjection) -> Any:
    """``realize``: draw the projection through the research visual coordinator.

    Builds one Matplotlib Figure whose top-level layout separates structural
    regions (primary/secondary/detail) from scientific panels
    (population/coverage/examples), then delegates each panel to a private
    rendering helper. The examples panel uses a nested ``subgridspec(2, 4)`` so
    one semantic panel realizes through 8 Axes (Panel != Axes).

    Uses explicit object-oriented Matplotlib operations and applies the
    figure's controlled presentation defaults (P3-T16/P3-T17).
    """
    import matplotlib.pyplot as plt
    from matplotlib import gridspec

    data = cast(HpcPlaceSummaryData, projection.content)
    binding = _validate_panel_region_binding(_PANEL_TO_REGION, _SEMANTIC_PANELS, _REQUIRED_REGIONS)

    figure = plt.figure()
    # Top-level structural topology: primary|secondary on the first row,
    # detail (examples) spanning the full second row.
    gs = gridspec.GridSpec(2, 2, figure=figure, height_ratios=[1, 1], width_ratios=[1, 1])

    axes = {
        "population": figure.add_subplot(gs[0, 0] if binding["population"] == "primary" else gs[0, 1]),
        "coverage": figure.add_subplot(gs[0, 0] if binding["coverage"] == "primary" else gs[0, 1]),
    }
    detail_spec = gs[1, :]
    _render_population(axes["population"], data)
    _render_coverage(axes["coverage"], data)
    _render_examples(figure, detail_spec, data)
    figure.suptitle("HPC place-field summary")
    return figure


def _render_population(ax: Any, data: HpcPlaceSummaryData) -> None:
    """Population panel: distribution of spatial selectivity across valid cells."""
    si = data.population_spatial_information
    ax.hist(si, bins=min(20, len(si) or 1), color="#4a76a8", edgecolor="white")
    ax.set_xlabel("spatial information (bits/spike)")
    ax.set_ylabel("cell count")
    ax.set_title("Population — spatial selectivity")


def _render_coverage(ax: Any, data: HpcPlaceSummaryData) -> None:
    """Coverage panel: spatial distribution of authoritative field centres."""
    domain = data.domain
    ax.set_xlim(0, domain.spatial_extent_x)
    ax.set_ylim(0, domain.spatial_extent_y)
    for row, col in data.selected_field_centres:
        x, y = domain.row_col_to_xy(row, col)
        ax.plot([x], [y], marker="o", markersize=4, color=_FIELD_CENTRE_COLOR, linestyle="none")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("Coverage — selected field centres")


def _render_examples(figure: Any, detail_spec: Any, data: HpcPlaceSummaryData) -> None:
    """Examples panel: highest-SI exemplars through a nested 2×4 subgridspec.

    One semantic panel realizes through 8 Matplotlib Axes
    (``subgridspec(2, 4)``), proving Panel != Axes (P3-T14). Each example rate
    map is normalized to its own local value domain (per-cell normalization,
    versioned visual semantics — P3-T11), so the panels compare spatial field
    shape rather than absolute magnitude across cells.
    """
    import numpy as np

    rows, cols = 2, 4
    sub = detail_spec.subgridspec(rows, cols)

    height = data.domain.height
    width = data.domain.width
    for index, cell_id in enumerate(data.selected_cell_ids):
        row, col = divmod(index, cols)
        ax = figure.add_subplot(sub[row, col])
        rate_map = np.asarray(data.selected_rate_maps[index], dtype=float).reshape(height, width)
        # Per-cell local value domain: compare field shape, not magnitude.
        vmax = float(rate_map.max()) if rate_map.size else 0.0
        ax.imshow(rate_map, origin="lower", cmap=_EXAMPLE_CMAP, vmin=0.0, vmax=vmax, aspect="equal")
        ax.set_title(cell_id, fontsize=8)
        ax.set_xticks([])
        ax.set_yticks([])


# ---------------------------------------------------------------------------
# FigureSpec
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class HpcPlaceSummaryFigure:
    """The ``figure:hpc-place-summary/v1`` reusable scientific figure.

    A registered ``DiscoverableDefinition`` (``ref`` + ``kind = "figure"``) with
    projection and visual partitions, contributed to the ordinary component
    catalogue by the research figure provider. All HPC-specific semantics live
    here (research-owned); the framework spine is unchanged (P3-T1/T20/G17).
    """

    ref: ComponentRef = field(default_factory=lambda: ComponentRef.parse(HPC_PLACE_SUMMARY_REF))
    kind: str = field(default=FIGURE_KIND)
    projection: _ProjectionPartition = field(
        default_factory=lambda: _ProjectionPartition(
            semantics_version=_PROJECTION_SEMANTICS_VERSION,
            preparation_version=_PREPARATION_VERSION,
            requirement=_INPUT_REQUIREMENT,
            prepare=_prepare_hpc_place_summary,
            select=_select_hpc_cells,
        )
    )
    visual: _VisualPartition = field(
        default_factory=lambda: _VisualPartition(
            semantics_version=_VISUAL_SEMANTICS_VERSION,
            realize=_realize_hpc_place_summary,
        )
    )
    defaults: _DefaultsPartition = field(
        default_factory=lambda: _DefaultsPartition(rc_params=dict(_DEFAULT_RC_PARAMS))
    )


#: The canonical HPC place-summary figure instance contributed by the provider.
HPC_PLACE_SUMMARY_FIGURE: FigureSpec = HpcPlaceSummaryFigure()


__all__ = [
    "HPC_ANALYSIS_CONTRACT",
    "HPC_PLACE_SUMMARY_FIGURE",
    "HPC_PLACE_SUMMARY_REF",
    "HpcPlaceSummaryData",
    "HpcPlaceSummaryFigure",
]
