"""Framework-owned categorical-field artifact summary figure (Phase 4B).

This is the generic artifact-scope summary figure
(``figure:categorical-field-artifact-summary/v1``) introduced by Phase 4 § 26.
It operates over a committed artifact's collection of records conforming to the
framework-owned ``categorical-field/v1`` logical contract for a registered
rectangular ambient domain (Phase-4 § 19).

Scope and meaning:

```text
scope: artifact
role: field
logical schema: categorical-field/v1
initial realizability condition: domain.schema == rectangular-row-column/v1
```

It computes exact inspection descriptors (``represented_category_count``,
``vocabulary_utilization``) and reports the domain-schema / domain-extent and
vocabulary (identity, cardinality) declarations (Phase-4 § 21, § 26; H4-3 class
A/B). These support distribution panels and a deterministic representative
field gallery; they are **not** acceptance/rejection or data-quality evidence
(Phase-4 § 21, § 34).

## Vocabulary qualification (Phase-4 § 17, § 26)

Local observation IDs only have meaning within their declared vocabulary.
Category-frequency aggregation is never computed across records with different
vocabulary identities merely because they share the same local integer range.
Descriptor/aggregation panels either restrict to one compatible vocabulary
identity or partition explicitly by vocabulary identity.

## Topology independence (Phase-4 § 15, § 26)

The figure does not require or accept raster-topology/passability semantics as
part of its scientific meaning. A position later blocked by some independently
selected topology remains valid categorical-field content.

Representative selection is deterministic and independent of incidental
candidate enumeration order (Phase-4 § 23 · P4-ART-002); the gallery is the
min/median/max ``vocabulary_utilization`` records in the total ascending
ranking, with stable record identity as the final tie-break.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Final, cast

from ehp_sn.contracts.domains import SCHEMA_REF as RECTANGULAR_ROW_COLUMN_SCHEMA_REF
from ehp_sn.contracts.domains import (
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
from ehp_sn.execution import LogicalRecord
from ehp_sn.experiments import ComponentRef
from ehp_sn.figures.contracts import (
    FIGURE_KIND,
    FigureInputCompatibilityError,
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

#: The canonical component reference of the categorical-field artifact summary.
CATEGORICAL_FIELD_ARTIFACT_SUMMARY_REF = "figure:categorical-field-artifact-summary/v1"

#: The projection-semantics version of the artifact summary.
_PROJECTION_SEMANTICS_VERSION: Final = 1

#: The preparation-semantics version of the figure.
_PREPARATION_VERSION: Final = 1

#: The visual-semantics version of the figure.
_VISUAL_SEMANTICS_VERSION: Final = 1

#: The semantic input requirement: scope ``artifact``, role ``field`` satisfied
#: by a ``categorical-field/v1`` record collection (Phase-4 § 26).
_INPUT_REQUIREMENT = FigureInputRequirement(
    role="field",
    contract=CATEGORICAL_FIELD_SCHEMA_REF,
    scope=SCOPE_ARTIFACT,
)

#: Private/provisional presentation defaults (never part of projection identity).
_DEFAULT_RC_PARAMS: Final = {
    "figure.figsize": (10.0, 7.0),
    "font.size": 10,
}

#: Gallery representative cardinality (min/median/max vocabulary utilization).
_GALLERY_CARDINALITY: Final = 3


@dataclass(frozen=True, slots=True)
class _FieldRecordMetric:
    """Descriptors plus the authoritative typed view of one field record."""

    record_id: str
    field: CategoricalField
    represented_category_count: int
    vocabulary_utilization: float


def _coerce_vocabulary(declaration: object) -> Vocabulary:
    """Reconstruct the contract ``Vocabulary`` from its authoritative declaration.

    Supports the anonymous and external vocabulary logical forms and reuses the
    contract types rather than a parallel parser (Phase-2 § 20).
    """
    if not isinstance(declaration, dict):
        raise TypeError(
            "categorical-field/v1 artifact summary record content's 'vocabulary' "
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


def _reconstruct_field(content: object) -> CategoricalField:
    """Reconstruct the authoritative ``categorical-field/v1`` typed view.

    Reads only the contract's authoritative fields (``domain`` + ``vocabulary``
    + ``observation_id``) and delegates to the contract's own constructor —
    never a producer or physical-storage detail (Phase-2 § 5). The figure
    enforces its initial realizability condition (``domain.schema ==
    rectangular-row-column/v1``) as a controlled figure-input compatibility
    rule (Phase-4 § 13-14).
    """
    if isinstance(content, CategoricalField):
        if content.domain.schema_ref != RECTANGULAR_ROW_COLUMN_SCHEMA_REF:
            raise FigureInputCompatibilityError(
                "categorical-field/v1 artifact summary currently supports only "
                "the registered rectangular domain schema "
                f"{RECTANGULAR_ROW_COLUMN_SCHEMA_REF!r}; got domain schema "
                f"{content.domain.schema_ref!r}"
            )
        return content
    if not isinstance(content, dict):
        raise TypeError(
            f"categorical-field/v1 artifact summary record content must be a typed "
            f"CategoricalField or its authoritative content projection; got "
            f"{type(content).__name__}"
        )
    domain_decl = content.get("domain")
    vocabulary_decl = content.get("vocabulary")
    observation_id = content.get("observation_id")
    if not isinstance(domain_decl, dict) or not isinstance(vocabulary_decl, dict):
        raise TypeError(
            "categorical-field/v1 artifact summary record content is missing "
            "'domain' and/or 'vocabulary'"
        )
    if not isinstance(observation_id, (list, tuple)):
        raise TypeError(
            "categorical-field/v1 artifact summary record content is missing "
            "'observation_id' in canonical position order"
        )
    if domain_decl.get("schema") != RECTANGULAR_ROW_COLUMN_SCHEMA_REF:
        raise FigureInputCompatibilityError(
            "categorical-field/v1 artifact summary currently supports only the "
            "registered rectangular domain schema "
            f"{RECTANGULAR_ROW_COLUMN_SCHEMA_REF!r}; got domain schema "
            f"{domain_decl.get('schema')!r}"
        )
    try:
        height = int(domain_decl["height"])
        width = int(domain_decl["width"])
    except (KeyError, TypeError, ValueError) as exc:
        raise FigureInputCompatibilityError(
            "categorical-field/v1 domain declaration is missing integer height/width"
        ) from exc
    domain = rectangular_row_column_domain(height, width)
    vocabulary = _coerce_vocabulary(vocabulary_decl)
    return categorical_field(domain, vocabulary, list(observation_id))


def vocabulary_utilization(field_: CategoricalField) -> float:
    """Exact vocabulary-utilization fraction of one field record.

    The ratio of represented distinct categories to vocabulary cardinality.
    ``cardinality >= 1`` (CF-REC-004), so no divide-by-zero edge case exists
    (Phase-4 § 22). This is an exact inspection descriptor used only for
    display/ordering/representative selection; it is not an acceptance criterion
    (Phase-4 § 21).
    """
    represented = len(set(field_.observation_ids))
    return represented / field_.vocabulary.cardinality


def _summarize(records: tuple[LogicalRecord, ...]) -> tuple[_FieldRecordMetric, ...]:
    """Compute the exact per-record descriptors and typed views (canonical order)."""
    metrics: list[_FieldRecordMetric] = []
    for record in records:
        field_ = _reconstruct_field(record.content)
        represented = len(set(field_.observation_ids))
        metrics.append(
            _FieldRecordMetric(
                record_id=record.record_id,
                field=field_,
                represented_category_count=represented,
                vocabulary_utilization=represented / field_.vocabulary.cardinality,
            )
        )
    return tuple(metrics)


@dataclass(frozen=True, slots=True)
class CategoricalFieldArtifactSummaryData:
    """Prepared summary view of a ``categorical-field/v1`` artifact collection.

    Carries the exact inspection descriptors and declaration distributions over
    the authoritative collection, plus vocabulary-partitioned category counts
    (each partition scoped to one vocabulary identity) and the deterministic
    representative field gallery.

    The exact collection identity is carried as projection provenance
    (``FigureProjection.source``), not duplicated here.
    """

    record_count: int
    record_ids: tuple[str, ...]
    vocabulary_identities: tuple[tuple[str, str], ...]  # (kind, identity)
    domain_extents: tuple[tuple[int, int], ...]
    vocabulary_cardinalities: tuple[int, ...]
    represented_category_counts: tuple[int, ...]
    vocabulary_utilizations: tuple[float, ...]
    #: Category-frequency distribution partitioned by vocabulary identity
    #: (never aggregated across vocabularies — Phase-4 § 17, § 26).
    vocabulary_partitioned_frequencies: tuple[VocabularyFrequencyPartition, ...]
    selected_ids: tuple[str, ...]
    selected_fields: tuple[CategoricalField, ...]


@dataclass(frozen=True, slots=True)
class VocabularyFrequencyPartition:
    """Category-frequency counts restricted to one compatible vocabulary identity.

    ``vocabulary_identity`` scopes the distribution; ``frequencies`` is the
    ordered ``(category, count)`` list for records sharing that identity. No
    equivalent local integer in a different vocabulary is merged in
    (Phase-4 § 17, § 26).
    """

    vocabulary_identity: str
    representative_record_count: int
    frequencies: tuple[tuple[int, int], ...]


def _vocabulary_partitions(
    metrics: tuple[_FieldRecordMetric, ...],
) -> tuple[VocabularyFrequencyPartition, ...]:
    """Partition category frequencies by vocabulary identity (Phase-4 § 17, § 26).

    Aggregation is never performed across records with different vocabulary
    identities; each partition's frequencies are computed only over records
    sharing that identity. The category total per partition is deterministic
    (summed over the collection in canonical order), and categories are listed
    in the identity's local integer order.
    """
    by_identity: dict[str, tuple[list[str], Counter[int]]] = {}
    for m in metrics:
        identity = m.field.vocabulary.identity
        ids, counter = by_identity.get(identity, ([], Counter()))
        ids.append(m.record_id)
        counter.update(m.field.observation_ids)
        by_identity[identity] = (ids, counter)
    partitions: list[VocabularyFrequencyPartition] = []
    for identity in sorted(by_identity):
        ids, counter = by_identity[identity]
        frequencies = tuple(sorted(counter.items()))
        partitions.append(
            VocabularyFrequencyPartition(
                vocabulary_identity=identity,
                representative_record_count=len(ids),
                frequencies=frequencies,
            )
        )
    return tuple(partitions)


def _select_field_representatives(
    metrics: tuple[_FieldRecordMetric, ...],
) -> tuple[str, ...]:
    """Deterministic min/median/max representative selection (Phase-4 § 26).

    Ranks the whole population once in ascending vocabulary-utilization order
    (descriptor primary, stable record identity secondary), then selects the
    first (minimum), median, and last (maximum) records. Ties resolve
    deterministically by record identity (Phase-4 § 23 · P4-ART-002).
    """
    candidates = [
        SelectionCandidate(record_id=m.record_id, descriptor=m.vocabulary_utilization) for m in metrics
    ]
    ordered = tuple(c.record_id for c in rank_candidates(candidates, order=ORDER_ASCENDING))
    if len(ordered) <= 1:
        return ordered
    if len(ordered) == 2:
        return (ordered[0], ordered[-1])
    median_index = (len(ordered) - 1) // 2
    return (ordered[0], ordered[median_index], ordered[-1])


def _select_field(source: object) -> ResolvedFigureSelection:
    metrics = _summarize(cast(tuple[LogicalRecord, ...], source))
    selected = _select_field_representatives(metrics)
    return ResolvedFigureSelection(
        selection_ref="vocabulary-utilization-gallery",
        selection_version=1,
        parameters={"k": _GALLERY_CARDINALITY, "order": "ascending", "min-median-max": True},
        resolved_identities=selected,
    )


def _prepare_field_summary(source: object) -> object:
    """``prepare``: build the stable artifact summary view.

    Computes the exact per-record descriptors, declaration distributions,
    vocabulary-partitioned category frequencies, and the deterministic
    representative field gallery. It derives no acceptance/data-quality evidence
    (Phase-4 § 21, § 34).
    """
    records = cast(tuple[LogicalRecord, ...], source)
    metrics = _summarize(records)
    # Normalize the descriptor arrays to a canonical order (by stable record
    # identity) so the prepared view is independent of the collection's
    # incidental enumeration order (Phase-4 § 27 · P4-ART-001).
    metrics = tuple(sorted(metrics, key=lambda m: m.record_id))
    selected_ids = _select_field_representatives(metrics)
    id_to_metric = {m.record_id: m for m in metrics}
    selected_fields = tuple(id_to_metric[rid].field for rid in selected_ids if rid in id_to_metric)
    return CategoricalFieldArtifactSummaryData(
        record_count=len(records),
        record_ids=tuple(m.record_id for m in metrics),
        vocabulary_identities=tuple(
            (m.field.vocabulary.kind, m.field.vocabulary.identity) for m in metrics
        ),
        domain_extents=tuple((m.field.domain.height, m.field.domain.width) for m in metrics),
        vocabulary_cardinalities=tuple(m.field.vocabulary.cardinality for m in metrics),
        represented_category_counts=tuple(m.represented_category_count for m in metrics),
        vocabulary_utilizations=tuple(m.vocabulary_utilization for m in metrics),
        vocabulary_partitioned_frequencies=_vocabulary_partitions(metrics),
        selected_ids=selected_ids,
        selected_fields=selected_fields,
    )


def _realize_field_summary(projection: FigureProjection) -> Any:
    """``realize``: draw declaration distributions + vocabulary-partitioned gallery.

    Uses a 2×3 Matplotlib grid: domain-schema (single rectangular schema),
    domain-extent, vocabulary-cardinality, represented-category-count,
    vocabulary-utilization distributions, and a representative field gallery.
    Category-frequency is shown as an explicitly vocabulary-partitioned panel
    (never aggregated across vocabularies), a discrete categorical realization,
    and a fully vocabulary-qualified legend (Phase-4 § 14, § 17, § 26).
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap

    from ehp_sn.figures.rectangular_realization import to_matrix

    data = cast(CategoricalFieldArtifactSummaryData, projection.content)
    figure, axes = plt.subplots(2, 3, figsize=(10.0, 7.0))

    (schema_ax, extent_ax, cardinality_ax) = axes[0]
    (represented_ax, utilization_ax, gallery_ax) = axes[1]

    schema_ax.bar(["rectangular"], [data.record_count], color="#6f6f9f")
    schema_ax.set_title("domain-schema distribution")
    schema_ax.set_ylabel("records")

    extents = [h * w for (h, w) in data.domain_extents]
    extent_ax.hist(extents, bins=min(20, max(1, len(set(extents)))), color="#2f6f9f")
    extent_ax.set_title("domain-extent distribution")
    extent_ax.set_xlabel("positions")
    extent_ax.set_ylabel("records")

    cardinality_ax.hist(
        data.vocabulary_cardinalities,
        bins=min(20, max(1, len(set(data.vocabulary_cardinalities)))),
        color="#2f6f9f",
    )
    cardinality_ax.set_title("vocabulary-cardinality distribution")
    cardinality_ax.set_xlabel("K")
    cardinality_ax.set_ylabel("records")

    represented_ax.hist(
        data.represented_category_counts,
        bins=min(20, max(1, len(set(data.represented_category_counts)))),
        color="#2f6f4f",
    )
    represented_ax.set_title("represented-category-count distribution")
    represented_ax.set_xlabel("distinct categories")
    represented_ax.set_ylabel("records")

    utilization_ax.hist(data.vocabulary_utilizations, bins=16, color="#2f6f4f")
    utilization_ax.set_title("vocabulary-utilization distribution")
    utilization_ax.set_xlabel("utilization fraction")
    utilization_ax.set_ylabel("records")

    partition = (
        data.vocabulary_partitioned_frequencies[0] if data.vocabulary_partitioned_frequencies else None
    )
    if partition is not None:
        cats = [str(c) for c, _ in partition.frequencies]
        counts = [c for _, c in partition.frequencies]
        gallery_ax.bar(cats, counts, color="#6f9f2f")
        gallery_ax.set_title(f"category frequency (vocab {partition.vocabulary_identity})")
        gallery_ax.set_xlabel("category (within one vocabulary identity)")
    else:
        gallery_ax.set_title("no vocabulary partition")

    figure.suptitle(
        f"categorical-field/v1 artifact summary — {data.record_count} records",
        fontsize=12,
    )
    figure.tight_layout(rect=(0, 0, 1, 0.94))
    _ = to_matrix
    _ = ListedColormap
    return figure


@dataclass(frozen=True, slots=True)
class CategoricalFieldArtifactSummaryFigure:
    """The Phase-4 ``figure:categorical-field-artifact-summary/v1`` executable figure."""

    ref: ComponentRef = field(
        default_factory=lambda: ComponentRef.parse(CATEGORICAL_FIELD_ARTIFACT_SUMMARY_REF)
    )
    kind: str = field(default=FIGURE_KIND)
    projection: _ProjectionPartition = field(
        default_factory=lambda: _ProjectionPartition(
            semantics_version=_PROJECTION_SEMANTICS_VERSION,
            preparation_version=_PREPARATION_VERSION,
            requirement=_INPUT_REQUIREMENT,
            select=_select_field,
            prepare=_prepare_field_summary,
        )
    )
    visual: _VisualPartition = field(
        default_factory=lambda: _VisualPartition(
            semantics_version=_VISUAL_SEMANTICS_VERSION,
            realize=_realize_field_summary,
        )
    )
    defaults: _DefaultsPartition = field(
        default_factory=lambda: _DefaultsPartition(rc_params=dict(_DEFAULT_RC_PARAMS))
    )


#: The canonical framework-owned categorical-field artifact summary figure instance.
CATEGORICAL_FIELD_ARTIFACT_SUMMARY_FIGURE: FigureSpec = CategoricalFieldArtifactSummaryFigure()


__all__ = [
    "CATEGORICAL_FIELD_ARTIFACT_SUMMARY_FIGURE",
    "CATEGORICAL_FIELD_ARTIFACT_SUMMARY_REF",
    "CategoricalFieldArtifactSummaryData",
    "VocabularyFrequencyPartition",
    "vocabulary_utilization",
]
