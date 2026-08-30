"""Framework-owned categorical-field inspection figure (Phase 2 bootstrap slice).

This is the third concrete framework-owned figure introduced by Phase 2
(``figure:categorical-field-inspection/v1``). Its complete scientific meaning is
expressible exclusively through the framework-owned ``categorical-field/v1``
logical contract for a registered rectangular ambient domain (Phase-2 § 17-18).

The figure understands (for a ``domain.schema == rectangular-row-column/v1``):

```text
categorical-field/v1
record identity
complete ambient-domain declaration
vocabulary (kind, identity, cardinality)
observation_id in canonical ambient-position order
```

It must not understand or require:

```text
topology, passability, topology state ID, movement, connected components
assignment protocol, realization index, generation seed, ObsField variant
DungeonGen / ObsField / Maze-ND identities
```

(Phase-2 § 17, § 23.)

## Initial domain compatibility

``categorical-field/v1`` permits any registered ``ambient-domain/v1`` schema
(Phase-2 § 18). The initial FigureSpec supports records whose
``domain.schema == rectangular-row-column/v1`` (the currently registered schema);
any other domain schema is a controlled figure-input-compatibility failure. This
is expressed as a figure-owned compatibility rule inside ``prepare`` (a normal
FigureInputContract compatibility rule); no ``CompatibilityExpression``,
``PredicateDSL``, or ``DomainQueryLanguage`` is introduced (Phase-2 § 18).

## Vocabulary identity is scientific

Two records with the same domain, same integer observation IDs, and equal
cardinality but **different vocabulary identity** are scientifically distinct
(Phase-2 § 21, CF-REC-005). The figure maps ``vocabulary identity + observation
ID`` deterministically to a categorical display style; visual similarity never
implies semantic similarity (Phase-2 § 26). Both the anonymous and external
vocabulary forms are supported without requiring external semantic metadata to
render (Phase-2 § 20).

## Discrete, non-ordinal, category-preserving realization

Observation IDs are categorical labels, not ordinal magnitudes (Phase-2 § 24).
Realization uses a discrete categorical mapping (a ``ListedColormap`` with
``interpolation="nearest"`` and an explicit ``vmin/vmax`` over category
indices), so no continuous normalization or sequential colormap is applied and
no interpolated pseudo-category can appear between adjacent categories
(Phase-2 § 25). The category-preserving resampling policy is set explicitly and
is never inherited from ambient ``image.interpolation`` configuration
(Phase-2 § 25).

The shared rectangular-domain realization (:func:`ehp_sn.figures.rectangular_realization.to_matrix`)
is the single scientific row/column mapping (Phase-2 § 6): the figure performs
no independent transpose/reflection/reordering beyond the contract's canonical
``position_id(r, c) = r * width + c``.

## High-cardinality policy

The contract imposes no small upper bound on vocabulary cardinality (Phase-2
§ 27). The figure separates the *semantic categorical mapping* (every category
value remains represented in the raster regardless of legend size) from the
*legend/readability policy* (a full legend key is shown only for low
cardinality; for high cardinality an abbreviated/truncated legend is shown with
an explicit cardinality/truncation indication). Scientific category values are
never silently omitted merely because the legend is large.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final, cast

from ehp_sn.contracts.domains import SCHEMA_REF as RECTANGULAR_ROW_COLUMN_SCHEMA_REF
from ehp_sn.contracts.domains import (
    RectangularRowColumnDomain,
    rectangular_row_column_domain,
)
from ehp_sn.contracts.observations import SCHEMA_REF as CATEGORICAL_FIELD_SCHEMA_REF
from ehp_sn.contracts.observations import (
    AnonymousVocabulary,
    CategoricalField,
    ExternalVocabulary,
    Vocabulary,
    categorical_field,
)
from ehp_sn.experiments import ComponentRef
from ehp_sn.figures.contracts import (
    FIGURE_KIND,
    FigureInputCompatibilityError,
    FigureInputRequirement,
    FigureSpec,
    InspectionCapacityExceeded,
    _DefaultsPartition,
    _ProjectionPartition,
    _VisualPartition,
)
from ehp_sn.figures.projection import FigureProjection
from ehp_sn.figures.rectangular_realization import to_matrix

#: The canonical component reference of the categorical-field inspection figure.
CATEGORICAL_FIELD_INSPECTION_REF = "figure:categorical-field-inspection/v1"

#: The projection-semantics version of ``figure:categorical-field-inspection/v1``.
_PROJECTION_SEMANTICS_VERSION: Final = 1

#: The preparation-semantics version of the figure.
_PREPARATION_VERSION: Final = 1

#: The visual-semantics version of the figure.
_VISUAL_SEMANTICS_VERSION: Final = 1

#: The semantic input requirement: role ``field`` satisfied by
#: ``categorical-field/v1`` (Phase-2 § 17).
_INPUT_REQUIREMENT = FigureInputRequirement(
    role="field",
    contract=CATEGORICAL_FIELD_SCHEMA_REF,
)

#: Private/provisional presentation defaults (never part of projection identity).
_DEFAULT_RC_PARAMS: Final = {
    "figure.figsize": (6.0, 6.0),
    "font.size": 10,
}

#: Default number of category entries shown in a low-cardinality legend/key.
_LOW_CARDINALITY_LEGEND_LIMIT: Final = 12

#: The figure's supported operational inspection capacity: the number of
#: distinct category values the categorical realization can faithfully and
#: unambiguously distinguish. Each distinct category receives a distinct
#: intended display style (Phase-3 § 32, § 36 · SRF-019). The capacity is set to
#: 45 so that the real committed ObsField vocabulary
#: (``obs-vocabulary:anonymous-45/v1``, cardinality 45) is faithfully served;
#: a vocabulary whose cardinality exceeds this capacity cannot be faithfully
#: represented without silently collapsing distinct categories onto identical
#: styles, which is forbidden (§ 32), so it fails explicitly with
#: :class:`InspectionCapacityExceeded`. This is presentation/operational
#: capacity, not scientific record identity: it never affects
#: ``ProjectionIdentity`` or producer semantics (§ 36).
_OPERATIONAL_CATEGORY_CAPACITY: Final = 45


def _qualitative_palette(size: int) -> tuple[str, ...]:
    """Return a deterministic qualitative (categorical) palette of ``size`` colors.

    Uses a golden-angle hue rotation in HCL/HSL space — a standard technique for
    categorical colormaps — so the hues are spread as far apart as possible for
    unambiguous distinction while saturation and lightness are held constant
    (no ordinal/sequential magnitude implied). Every entry is distinct, so no
    distinct category value is ever silently mapped onto an identical intended
    display style (Phase-3 § 32 · SRF-019). The palette is deterministic for a
    fixed visual-semantics version and never makes colour part of the scientific
    vocabulary.
    """
    import colorsys

    golden_angle = 0.618033988749895  # fractions of one hue turn
    colors: list[str] = []
    for i in range(size):
        hue = (i * golden_angle) % 1.0
        r, g, b = colorsys.hls_to_rgb(hue, 0.55, 0.70)
        colors.append(f"#{int(round(r * 255)):02x}{int(round(g * 255)):02x}{int(round(b * 255)):02x}")
    return tuple(colors)


#: Base categorical display palette (deterministic; exactly one distinct colour
#: per supported category value, with the golden-angle hue spread for maximum
#: distinguishability).
_CATEGORY_PALETTE: Final = _qualitative_palette(_OPERATIONAL_CATEGORY_CAPACITY)


@dataclass(frozen=True, slots=True)
class CategoricalFieldInspectionData:
    """Framework-owned prepared structural view of one ``categorical-field/v1`` record.

    Carries exactly the authoritative contract structure the figure communicates
    (Phase-2 § 19):

    ``domain`` is the reconstructed canonical rectangular ambient domain;
    ``vocabulary_kind`` / ``vocabulary_identity`` / ``vocabulary_cardinality``
    are the resolved vocabulary declaration components; ``observation_ids`` is
    the total categorical assignment in canonical ambient-position order;
    ``represented_category_count`` is an optional exact inspection descriptor
    (the number of distinct category values actually present).

    The exact record identity is carried as projection provenance
    (``FigureProjection.source.record_id``), not duplicated here.
    """

    domain: RectangularRowColumnDomain
    vocabulary_kind: str
    vocabulary_identity: str
    vocabulary_cardinality: int
    observation_ids: tuple[int, ...]
    represented_category_count: int


def _coerce_vocabulary(declaration: object) -> Vocabulary:
    """Reconstruct the contract ``Vocabulary`` from its authoritative declaration.

    Supports the anonymous and external vocabulary logical forms
    (``categorical-field/v1`` § "Vocabulary contract") and reuses the contract
    types rather than a parallel parser (Phase-2 § 20).
    """
    if not isinstance(declaration, dict):
        raise TypeError(
            "categorical-field/v1 authoritative content projection's 'vocabulary' "
            "must be a declaration mapping"
        )
    kind = declaration.get("kind")
    cardinality = declaration.get("cardinality")
    if kind == "anonymous":
        identity = declaration.get("identity")
        if not isinstance(identity, str) or not identity:
            raise TypeError("anonymous vocabulary requires a non-empty string identity")
        return AnonymousVocabulary(identity=identity, cardinality=cast(int, cardinality))
    if kind == "external":
        ref = declaration.get("ref")
        identity = declaration.get("identity")
        if not isinstance(ref, str) or not ref:
            raise TypeError("external vocabulary requires a non-empty string ref")
        if not isinstance(identity, str) or not identity:
            raise TypeError("external vocabulary requires a resolved immutable identity")
        return ExternalVocabulary(ref=ref, identity=identity, cardinality=cast(int, cardinality))
    raise TypeError(f"unknown vocabulary kind {kind!r} (expected 'anonymous' or 'external')")


def _extract_authoritative_field(content: object) -> CategoricalFieldInspectionData:
    """Reconstruct the authoritative ``categorical-field/v1`` prepared view.

    Accepts either an already-typed :class:`CategoricalField` (producer/
    in-memory context) or the authoritative committed ``content()`` projection
    dictionary (``domain`` + ``vocabulary`` + ``observation_id``). It reads only
    the contract's authoritative fields and delegates to the contract's own
    constructor (:func:`categorical_field`) for validation and canonical
    position-order enforcement (Phase-2 § 5) — never a producer detail.

    The figure reads the canonical committed-instance field ``observation_id``
    (singular, per ``CF-REC-002``), matching the single validation authority
    (``contracts/validation.py``). It is not a compatibility layer for any
    obsolete/plural representation (Phase-2 § 4).
    """
    if isinstance(content, CategoricalField):
        field_: CategoricalField = content
    elif isinstance(content, dict):
        domain = content.get("domain")
        vocabulary = content.get("vocabulary")
        observation_id = content.get("observation_id")
        if not isinstance(domain, dict) or not isinstance(vocabulary, dict):
            raise TypeError(
                "categorical-field/v1 authoritative content projection is missing "
                "'domain' and/or 'vocabulary'"
            )
        if not isinstance(observation_id, (list, tuple)):
            raise TypeError(
                "categorical-field/v1 authoritative content projection is missing "
                "'observation_id' in canonical position order"
            )
        field_ = _build_typed(content)
    else:
        raise TypeError(
            f"categorical-field/v1 figure source must be a typed CategoricalField or its "
            f"authoritative content projection; got {type(content).__name__}"
        )

    represented = len(set(field_.observation_ids))
    _assert_operational_category_capacity(field_.vocabulary.cardinality)
    return CategoricalFieldInspectionData(
        domain=field_.domain,
        vocabulary_kind=field_.vocabulary.kind,
        vocabulary_identity=field_.vocabulary.identity,
        vocabulary_cardinality=field_.vocabulary.cardinality,
        observation_ids=tuple(field_.observation_ids),
        represented_category_count=represented,
    )


def _assert_operational_category_capacity(cardinality: int) -> None:
    """Deterministically reject a vocabulary the realization cannot faithfully render.

    The categorical realization gives every distinct category value a distinct
    intended display style, up to ``_OPERATIONAL_CATEGORY_CAPACITY``. A
    vocabulary larger than that cannot be faithfully distinguished without
    silently mapping distinct categories to identical styles — forbidden by
    Phase-3 § 32 — so it fails explicitly and deterministically via
    :class:`InspectionCapacityExceeded` (Phase-3 § 36 · SRF-019). This is
    presentation/operational capacity and never affects scientific record
    identity or ``ProjectionIdentity``.
    """
    if cardinality > _OPERATIONAL_CATEGORY_CAPACITY:
        raise InspectionCapacityExceeded(
            f"categorical-field/v1 inspection cannot faithfully represent "
            f"vocabulary cardinality {cardinality}: supported operational "
            f"capacity is {_OPERATIONAL_CATEGORY_CAPACITY} distinct categories. "
            f"Refusing to silently collapse distinct categories onto identical "
            f"display styles."
        )


def _build_typed(content: dict) -> CategoricalField:
    """Reconstruct the typed :class:`CategoricalField` from a content projection.

    Validates the domain schema compatibility rule (rectangular-row-column only,
    Phase-2 § 18), then delegates to the contract's own constructor, which
    enforces every ``CF-REC-*`` invariant from the authoritative fields.
    """
    domain_decl = content["domain"]
    if not isinstance(domain_decl, dict):
        raise FigureInputCompatibilityError(
            "categorical-field/v1 inspection requires a complete ambient-domain declaration"
        )
    if domain_decl.get("schema") != RECTANGULAR_ROW_COLUMN_SCHEMA_REF:
        raise FigureInputCompatibilityError(
            f"categorical-field/v1 inspection currently supports only the registered "
            f"rectangular domain schema {RECTANGULAR_ROW_COLUMN_SCHEMA_REF!r}; "
            f"got domain schema {domain_decl.get('schema')!r}"
        )
    try:
        height = int(domain_decl["height"])
        width = int(domain_decl["width"])
    except (KeyError, TypeError, ValueError) as exc:
        raise FigureInputCompatibilityError(
            "categorical-field/v1 domain declaration is missing integer height/width"
        ) from exc
    domain = rectangular_row_column_domain(height, width)
    vocabulary = _coerce_vocabulary(content["vocabulary"])
    return categorical_field(domain, vocabulary, list(content["observation_id"]))


def _prepare_authoritative_field(source: object) -> object:
    """``prepare``: convert the validated authoritative source to a stable typed view.

    The prepared view carries the authoritative field structure derived from the
    contract's own constructor. It derives no new scientific conclusion beyond
    the authoritative contract; only an exact inspection descriptor (represented
    category count) is included to help explain the individual record
    (Phase-2 § 19). The exact record identity is carried as projection
    provenance, not duplicated here.
    """
    return _extract_authoritative_field(source)


def _vocabulary_style_offset(vocabulary_identity: str) -> int:
    """A deterministic, presentation-only offset derived from vocabulary identity.

    Observation ID meaning is scoped by vocabulary identity (Phase-3 § 30 ·
    SRF-012): equal integer IDs under different vocabularies are not
    scientifically equivalent. The intended display style is therefore a
    deterministic function of ``(vocabulary identity, observation ID)`` — the
    identity contributes a fixed offset into the palette so that the same ID in
    a different vocabulary receives a different intended style. The offset is
    confined to visual semantics: it never changes scientific vocabulary or
    record identity, and visual similarity never implies semantic similarity
    across vocabularies (Phase-3 § 31). Each distinct category within one
    vocabulary still receives a distinct style (capacity is enforced in
    ``prepare``).

    The offset uses a stable, cross-process deterministic digest (CRC-32) rather
    than Python's salted built-in ``hash()``, so the intended display style is
    reproducible across interpreter runs and environments (categorical visual
    stability, Phase-3 § 31).
    """
    import binascii

    return binascii.crc32(vocabulary_identity.encode("utf-8")) % _OPERATIONAL_CATEGORY_CAPACITY


def _category_color(category: int, vocabulary_identity: str) -> str:
    """Return the deterministic display colour for ``(vocabulary, category)``.

    The style is anchored to the fixed palette at
    ``(vocabulary offset + category)``, so it is a deterministic function of the
    vocabulary identity and the observation ID (Phase-3 § 31 · SRF-012).
    ``prepare`` has already rejected a vocabulary whose cardinality exceeds
    ``_OPERATIONAL_CATEGORY_CAPACITY``, so within one vocabulary each distinct
    category maps to a distinct style and no distinct category is silently
    collapsed onto an identical style (Phase-3 § 32). The mapping belongs to
    visual semantics and never makes colour part of the scientific vocabulary.
    """
    return _CATEGORY_PALETTE[
        (_vocabulary_style_offset(vocabulary_identity) + category) % _OPERATIONAL_CATEGORY_CAPACITY
    ]


def _realize_field_inspection(projection: FigureProjection) -> Any:
    """``realize``: draw the projection as a direct Matplotlib Figure.

    Uses one Figure and one Axes with a discrete categorical raster over the
    shared canonical rectangular-domain mapping (Phase-2 § 6, § 22). Category
    values are drawn through an explicit ``ListedColormap`` with
    ``interpolation="nearest"`` — no continuous interpolation, no ordinal
    colourmap, no pseudo-category (Phase-2 § 24-25). Presentation parameters
    (origin, aspect) are set explicitly and unaffected by ambient defaults.

    A category legend/key is shown for low cardinality; for high cardinality it
    is abbreviated with an explicit cardinality/truncation indication while all
    category values remain present in the raster (Phase-2 § 27).
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap

    data = cast(CategoricalFieldInspectionData, projection.content)
    domain = data.domain
    _assert_operational_category_capacity(data.vocabulary_cardinality)

    # Shared canonical row/column mapping (Phase-2 § 6).
    matrix = to_matrix(domain, list(data.observation_ids))

    figure, axes = plt.subplots(1, 1)
    cmap = ListedColormap(
        [_category_color(c, data.vocabulary_identity) for c in range(data.vocabulary_cardinality)]
    )
    image = axes.imshow(
        matrix,
        cmap=cmap,
        interpolation="nearest",
        aspect="equal",
        origin="upper",
        vmin=0,
        vmax=data.vocabulary_cardinality - 1,
    )
    axes.set_title(f"Categorical field — {domain.height}×{domain.width} categorical assignment")
    axes.set_xlabel("column")
    axes.set_ylabel("row")
    axes.set_xticks(range(domain.width))
    axes.set_yticks(range(domain.height))

    # Legend / readability policy (Phase-2 § 27), separated from the semantic
    # categorical mapping.
    if data.vocabulary_cardinality <= _LOW_CARDINALITY_LEGEND_LIMIT:
        _draw_full_legend(figure, axes, data)
    else:
        _draw_abbreviated_legend(figure, axes, data)
    _ = image
    return figure


def _draw_full_legend(figure: Any, axes: Any, data: CategoricalFieldInspectionData) -> None:
    """Draw a full categorical category key (low cardinality)."""
    import matplotlib.patches as mpatches

    handles = [
        mpatches.Patch(color=_category_color(c, data.vocabulary_identity), label=f"{c}")
        for c in range(data.vocabulary_cardinality)
    ]
    figure.legend(
        handles=handles,
        loc="lower center",
        ncol=min(data.vocabulary_cardinality, 8),
        frameon=False,
    )
    _ = axes


def _draw_abbreviated_legend(figure: Any, axes: Any, data: CategoricalFieldInspectionData) -> None:
    """Draw an explicitly abbreviated category key (high cardinality).

    All scientific category values remain represented in the raster; only the
    human-readable legend is abbreviated, with an explicit cardinality /
    truncation indication (Phase-2 § 27).
    """
    import matplotlib.patches as mpatches

    shown = list(range(_LOW_CARDINALITY_LEGEND_LIMIT))
    handles = [
        mpatches.Patch(color=_category_color(c, data.vocabulary_identity), label=f"{c}") for c in shown
    ]
    handles.append(
        mpatches.Patch(
            color="none",
            label=f"… {data.vocabulary_cardinality - _LOW_CARDINALITY_LEGEND_LIMIT} more "
            f"(K={data.vocabulary_cardinality})",
        )
    )
    figure.legend(handles=handles, loc="lower center", ncol=8, frameon=False)
    _ = axes


@dataclass(frozen=True, slots=True)
class CategoricalFieldInspectionFigure:
    """The Phase-2 ``figure:categorical-field-inspection/v1`` executable figure.

    A registered ``DiscoverableDefinition`` (``ref`` + ``kind = "figure"``) with
    projection and visual partitions. It participates in the ordinary component
    catalogue; there is no parallel figure registry.
    """

    ref: ComponentRef = field(
        default_factory=lambda: ComponentRef.parse(CATEGORICAL_FIELD_INSPECTION_REF)
    )
    kind: str = field(default=FIGURE_KIND)
    projection: _ProjectionPartition = field(
        default_factory=lambda: _ProjectionPartition(
            semantics_version=_PROJECTION_SEMANTICS_VERSION,
            preparation_version=_PREPARATION_VERSION,
            requirement=_INPUT_REQUIREMENT,
            prepare=_prepare_authoritative_field,
        )
    )
    visual: _VisualPartition = field(
        default_factory=lambda: _VisualPartition(
            semantics_version=_VISUAL_SEMANTICS_VERSION,
            realize=_realize_field_inspection,
            # The categorical colour mapping is scientific visual semantics: a
            # presentation policy must not silently swap in a continuous or
            # sequential colormap. ``image.cmap`` is therefore protected.
            protected_rc_params=frozenset({"image.cmap"}),
        )
    )
    defaults: _DefaultsPartition = field(
        default_factory=lambda: _DefaultsPartition(rc_params=dict(_DEFAULT_RC_PARAMS))
    )


#: The canonical framework-owned categorical-field inspection figure instance.
CATEGORICAL_FIELD_INSPECTION_FIGURE: FigureSpec = CategoricalFieldInspectionFigure()


__all__ = [
    "CATEGORICAL_FIELD_INSPECTION_FIGURE",
    "CATEGORICAL_FIELD_INSPECTION_REF",
    "CategoricalFieldInspectionData",
]
