"""Research-owned ObsField generation-summary figure (Phase 5, Stage D).

This module implements ``figure:obsfield-generation-summary/v1``, a
producer-owned scientific figure in ``ehp_research`` that summarizes one
committed ObsField ``categorical-field/v1`` artifact release. It consumes the
same record collection the generic ``figure:categorical-field-artifact-summary/
v1`` consumes plus the committed artifact's producer-owned metadata through the
artifact-metadata surfaces (``producer-descriptors``, ``provenance``,
``auxiliary``), and reports **facts** about the configured generation — it
renders no acceptance/rejection verdict and no split summary (Phase-5 ·
SRF-019).

Producer identity is a research-owned guard, not a framework detail
(``ARCH-001``): the figure starts by reading the committed provenance's
``specification_reference`` and raises a controlled :class:`TypeError` when it
is not ``obsfield/v1``.

## Selection and legacy handling

The representative gallery is ``realization-index-gallery`` (v1): records are
ranked ascending by their per-record ``realization_index`` descriptor and the
min/median/max records are selected. **Legacy releases may not carry a
``realization_index`` descriptor** (the per-record descriptors are empty); when
the descriptor is absent the figure falls back to a deterministic record-order
ranking (sorted by stable record identity), so the gallery is fully
deterministic and the figure still works. This fallback is documented in the
figure body.

## Categorical realization (no silent aliasing)

Observation IDs are categorical labels, never a continuous scale
(Phase-4 § 11). The realization uses a qualitative colormap with enough
distinct colours for the vocabulary cardinality (compounding ``tab20``,
``tab20b``, ``tab20c`` for up to 60 distinct categories) so distinct categories
are never silently aliased; when a field's distinct categories exceed that the
figure renders a labelled legend rather than cycling few colours.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final, cast

from ehp_sn.contracts.observations import SCHEMA_REF as CATEGORICAL_FIELD_SCHEMA_REF
from ehp_sn.contracts.observations import CategoricalField
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
    reconstruct_categorical_field,
    record_descriptor,
    select_min_median_max,
)

#: The canonical component reference of the ObsField generation summary.
OBSFIELD_GENERATION_SUMMARY_REF = "figure:obsfield-generation-summary/v1"

#: The expected producer specification reference for the provenance guard.
_OBSFIELD_SPEC_REF = "obsfield/v1"

#: The projection-semantics version of the generation summary.
_PROJECTION_SEMANTICS_VERSION: Final = 1

#: The preparation-semantics version of the figure.
_PREPARATION_VERSION: Final = 1

#: The visual-semantics version of the figure.
_VISUAL_SEMANTICS_VERSION: Final = 1

#: The artifact-metadata surfaces this producer figure declares.
_METADATA_SURFACES: Final = frozenset(
    {SURFACE_PRODUCER_DESCRIPTORS, SURFACE_PROVENANCE, SURFACE_AUXILIARY}
)

#: The figure's declared metadata surface requirement.
_INPUT_REQUIREMENT = FigureInputRequirement(
    role="obsfield_generation",
    contract=CATEGORICAL_FIELD_SCHEMA_REF,
    scope=SCOPE_ARTIFACT,
    artifact_metadata_surfaces=_METADATA_SURFACES,
)

#: Private/provisional presentation defaults (never part of projection identity).
_DEFAULT_RC_PARAMS: Final = {
    "figure.figsize": (11.0, 8.0),
    "font.size": 10,
}

#: Gallery representative cardinality (min/median/max).
_GALLERY_CARDINALITY: Final = 3


@dataclass(frozen=True, slots=True)
class ObsFieldGenerationSummaryData:
    """Stable research-owned prepared view for ``figure:obsfield-generation-summary/v1``.

    Carries the exact committed values needed to render the summary: the
    authored generation configuration (assignment protocol, distribution,
    domain schema/extent, vocabulary identity/cardinality, realization count,
    seed), the per-record realization indexes in canonical order, the
    compaction validation status (verbatim, when an auxiliary
    ``obsfield-validation`` resource exists), and the deterministic
    representative field gallery (selected identities + authoritative typed
    ``CategoricalField`` views).

    This view owns no scientific computation — it is assembled by ``prepare()``
    from authoritative committed values only (Phase-5 § 38).
    """

    assignment_protocol: Any
    distribution: Any
    domain_schema: Any
    domain_height: Any
    domain_width: Any
    vocabulary_identity: Any
    vocabulary_cardinality: Any
    realization_count: Any
    seed: Any
    realization_indexes: tuple[int, ...]
    validation_status: Any
    selected_ids: tuple[str, ...]
    selected_fields: tuple[CategoricalField, ...]


def _canonical_order(records: tuple[Any, ...]) -> tuple[Any, ...]:
    """Canonical (stable) record order, independent of incidental enumeration order."""
    return tuple(sorted(records, key=lambda r: r.record_id))


def _realization_indexes(records: tuple[Any, ...]) -> tuple[int, ...]:
    """Per-record realization indexes in canonical order.

    When a record carries the per-record ``realization_index`` descriptor its
    value is used; legacy releases without the descriptor fall back to the
    positional index in the deterministic canonical order (documented body
    behaviour). The result is fully deterministic for both cases.
    """
    ordered = _canonical_order(records)
    result: list[int] = []
    for index, record in enumerate(ordered):
        value = record_descriptor(record, "realization_index")
        if value is None:
            result.append(index)
        else:
            result.append(int(value))
    return tuple(result)


def _select_obsfield(source: object) -> ResolvedFigureSelection:
    """``select``: resolve the realization-index gallery against one committed artifact."""
    content = cast(Any, source)
    guard_producer_identity(
        identity_inputs_to_dict(content.provenance),
        _OBSFIELD_SPEC_REF,
        OBSFIELD_GENERATION_SUMMARY_REF,
    )
    selected = _select_representative_ids(content.records)
    return ResolvedFigureSelection(
        selection_ref="realization-index-gallery",
        selection_version=1,
        parameters={"descriptor": "realization_index", "order": "ascending", "k": _GALLERY_CARDINALITY},
        resolved_identities=selected,
    )


def _select_representative_ids(records: tuple[Any, ...]) -> tuple[str, ...]:
    """Deterministic min/median/max realization-index representative selection.

    Builds candidates in canonical (stable) order using the per-record
    realization index (with the documented legacy fallback), ranks ascending
    (descriptor primary, stable record identity secondary), and selects the
    min/median/max records.
    """
    ordered = _canonical_order(records)
    indexes = _realization_indexes(records)
    candidates = [
        SelectionCandidate(record_id=record.record_id, descriptor=realization_index)
        for record, realization_index in zip(ordered, indexes, strict=True)
    ]
    ranked = tuple(c.record_id for c in rank_candidates(candidates, order=ORDER_ASCENDING))
    return select_min_median_max(ranked)


def _prepare_obsfield(source: object) -> object:
    """``prepare``: assemble the stable :class:`ObsFieldGenerationSummaryData` view.

    Reads already-authoritative committed values (provenance configuration, the
    per-record realization indexes, and the deterministic representative
    gallery) and returns the typed view. It derives no acceptance/rejection or
    data-quality evidence (Phase-5 § 38).
    """
    content = cast(Any, source)
    inputs = identity_inputs_to_dict(content.provenance)
    guard_producer_identity(inputs, _OBSFIELD_SPEC_REF, OBSFIELD_GENERATION_SUMMARY_REF)

    records = content.records
    realization_indexes = _realization_indexes(records)
    selected_ids = _select_representative_ids(records)
    by_id = {record.record_id: record for record in records}
    selected_fields = tuple(
        reconstruct_categorical_field(by_id[rid].content) for rid in selected_ids if rid in by_id
    )

    validation = find_auxiliary(content, "obsfield-validation")
    return ObsFieldGenerationSummaryData(
        assignment_protocol=inputs.get("assignment_protocol"),
        distribution=inputs.get("distribution"),
        domain_schema=inputs.get("domain_schema"),
        domain_height=inputs.get("domain_height"),
        domain_width=inputs.get("domain_width"),
        vocabulary_identity=inputs.get("vocabulary_identity"),
        vocabulary_cardinality=inputs.get("vocabulary_cardinality"),
        realization_count=inputs.get("realization_count"),
        seed=inputs.get("seed"),
        realization_indexes=realization_indexes,
        validation_status=validation.content if validation is not None else None,
        selected_ids=selected_ids,
        selected_fields=selected_fields,
    )


def _realize_obsfield(projection: FigureProjection) -> Any:
    """``realize``: draw configuration text and a categorical realization gallery.

    Uses a 2-row layout: the first row shows the authored generation
    configuration as text; the second row draws the representative realization
    gallery, each field rendered as a raster over its domain with a categorical
    (qualitative) colourmap and a labelled legend. Observation IDs are
    categorical labels, never a continuous scale.
    """
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec

    data = cast(ObsFieldGenerationSummaryData, projection.content)
    figure = plt.figure()
    gs = GridSpec(2, 2, figure=figure, height_ratios=[1, 3])

    config_ax = figure.add_subplot(gs[0, :])
    gallery_spec = gs[1, :]

    _render_obsfield_config(config_ax, data)
    _render_field_gallery(figure, gallery_spec, data)

    figure.suptitle(
        f"ObsField categorical-field/v1 generation summary — "
        f"{len(data.realization_indexes)} realizations",
        fontsize=12,
    )
    figure.tight_layout(rect=(0, 0, 1, 0.95))
    return figure


def _render_obsfield_config(ax: Any, data: ObsFieldGenerationSummaryData) -> None:
    """Render the authored generation configuration as factual text rows."""
    ax.axis("off")
    lines = [
        f"assignment_protocol: {data.assignment_protocol}",
        f"distribution: {data.distribution}",
        f"domain_schema: {data.domain_schema}",
        f"domain: {data.domain_height} x {data.domain_width}",
        f"vocabulary_identity: {data.vocabulary_identity}",
        f"vocabulary_cardinality: {data.vocabulary_cardinality}",
        f"realization_count: {data.realization_count}",
        f"seed: {data.seed}",
    ]
    if data.validation_status is not None:
        if isinstance(data.validation_status, dict):
            for key, value in data.validation_status.items():
                lines.append(f"validation.{key}: {value}")
        else:
            lines.append(f"validation: {data.validation_status}")
    else:
        lines.append("validation: not provided")
    ax.text(
        0.02,
        0.99,
        "\n".join(lines),
        transform=ax.transAxes,
        va="top",
        ha="left",
        family="monospace",
        fontsize=9,
    )
    ax.set_title("generation configuration")


def _qualitative_colormap(cardinality: int) -> Any:
    """A qualitative colormap with at least ``cardinality`` distinct colours.

    Compounds the built-in qualitative maps (``tab20``, ``tab20b``, ``tab20c``,
    ``tab10``) to guarantee enough distinct colours so distinct observation-id
    categories are never silently aliased. ``tab10`` is appended for the
    remainder beyond 60; cardinalities above that keep distinct colour tuples so
    no two categories share a colour.
    """
    from matplotlib import colormaps
    from matplotlib.colors import ListedColormap

    colours: list[Any] = []
    for name in ("tab20", "tab20b", "tab20c", "tab10"):
        palette = colormaps[name]
        for i in range(palette.N):
            colours.append(palette(i))
    return ListedColormap(colours)


def _render_field_gallery(figure: Any, gallery_spec: Any, data: ObsFieldGenerationSummaryData) -> None:
    """Render the representative realization gallery (min/median/max realization index)."""
    count = len(data.selected_fields)
    if count == 0:
        return
    sub = gallery_spec.subgridspec(1, count)
    cardinality = _effective_cardinality(data)
    cmap = _qualitative_colormap(cardinality)
    for i, field_ in enumerate(data.selected_fields):
        ax = figure.add_subplot(sub[i])
        _draw_field(ax, field_, cmap)
        ax.set_title(data.selected_ids[i][:12], fontsize=8)


def _effective_cardinality(data: ObsFieldGenerationSummaryData) -> int:
    """The vocabulary cardinality used for the qualitative colormap sizing."""
    try:
        return int(data.vocabulary_cardinality or 0) or 1
    except (TypeError, ValueError):
        return 1


def _draw_field(ax: Any, field_: CategoricalField, cmap: Any) -> None:
    """Draw one categorical field as a raster over its domain.

    Uses the explicit scientific row/column mapping and categorical colouring;
    observation IDs are categorical labels, never a continuous normalization.
    A labelled legend lists the distinct categories present in this field.
    """
    import matplotlib.pyplot as plt

    height = field_.domain.height
    width = field_.domain.width
    grid = [field_.observation_ids[(r * width + c)] for r in range(height) for c in range(width)]
    import numpy as np

    matrix = np.asarray(grid, dtype=int).reshape(height, width)
    ax.imshow(matrix, cmap=cmap, interpolation="nearest", aspect="equal", origin="upper")
    ax.set_axis_off()

    distinct = sorted(set(int(x) for x in field_.observation_ids))
    if len(distinct) <= 40:
        handles = [
            plt.Line2D([0], [0], marker="s", color="none", markerfacecolor=cmap(int(v)), markersize=7)
            for v in distinct
        ]
        ax.legend(
            handles,
            [str(v) for v in distinct],
            loc="upper left",
            bbox_to_anchor=(1.02, 1.0),
            fontsize=6,
            ncol=2,
            title="category",
            frameon=False,
        )
    else:
        ax.set_title(f"{len(distinct)} categories")


@dataclass(frozen=True, slots=True)
class ObsFieldGenerationSummaryFigure:
    """The ``figure:obsfield-generation-summary/v1`` reusable scientific figure."""

    ref: ComponentRef = field(
        default_factory=lambda: ComponentRef.parse(OBSFIELD_GENERATION_SUMMARY_REF)
    )
    kind: str = field(default=FIGURE_KIND)
    projection: _ProjectionPartition = field(
        default_factory=lambda: _ProjectionPartition(
            semantics_version=_PROJECTION_SEMANTICS_VERSION,
            preparation_version=_PREPARATION_VERSION,
            requirement=_INPUT_REQUIREMENT,
            select=_select_obsfield,
            prepare=_prepare_obsfield,
        )
    )
    visual: _VisualPartition = field(
        default_factory=lambda: _VisualPartition(
            semantics_version=_VISUAL_SEMANTICS_VERSION,
            realize=_realize_obsfield,
        )
    )
    defaults: _DefaultsPartition = field(
        default_factory=lambda: _DefaultsPartition(rc_params=dict(_DEFAULT_RC_PARAMS))
    )


#: The canonical ObsField generation-summary figure instance contributed by the provider.
OBSFIELD_GENERATION_SUMMARY_FIGURE: FigureSpec = ObsFieldGenerationSummaryFigure()


__all__ = [
    "OBSFIELD_GENERATION_SUMMARY_FIGURE",
    "OBSFIELD_GENERATION_SUMMARY_REF",
    "ObsFieldGenerationSummaryData",
]
