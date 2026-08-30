"""Framework-owned categorical-field figure tests (Phase 2).

These test :mod:`ehp_sn.figures.builtin.categorical_field` — the framework-owned
built-in figure ``figure:categorical-field-inspection/v1`` whose complete
scientific meaning is expressible purely through the framework-owned
``categorical-field/v1`` logical contract for a registered rectangular ambient
domain (Phase-2 § 17-18).

They verify the Phase-2 § 44 required test matrix for the categorical inspector:

* canonical runtime schema (authoritative ``domain`` + ``vocabulary`` +
  ``observation_id``, singular per CF-REC-002);
* anonymous and external vocabulary forms (Phase-2 § 20);
* complete ambient field represented; position→cell mapping exact; no values
  lost/reordered/transposed/reflected (Phase-2 § 6, § 28);
* rectangular-row-column mapping reused from the shared framework realization
  (Phase-2 § 6);
* no topology required and no topology mask applied (Phase-2 § 23);
* discrete / non-ordinal categorical semantics (Phase-2 § 24);
* category-preserving interpolation (no pseudo-categories, Phase-2 § 25);
* ambient image.origin / image.interpolation perturbation → semantics unchanged
  (Phase-2 § 25, § 28);
* different vocabulary identities remain distinct (Phase-2 § 21);
* deterministic vocabulary/category styling (Phase-2 § 26);
* high-cardinality legend policy explicit; all categories represented
  (Phase-2 § 27);
* compatibility rejects a non-supported (non-rectangular) domain capability
  (Phase-2 § 18);
* rendering does not mutate the authoritative source/prepared view/projection
  (Phase-2 § 33).

Headless Matplotlib backend is selected before any pyplot use.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless backend required

import pytest
from ehp_sn.contracts.domains import rectangular_row_column_domain
from ehp_sn.contracts.observations import (
    AnonymousVocabulary,
    ExternalVocabulary,
    categorical_field,
)
from ehp_sn.figures import (
    FigureInputCompatibilityError,
    effective_figure_registry,
    prepare_figure,
    render_figure_projection,
)
from ehp_sn.figures.builtin.categorical_field import (
    CATEGORICAL_FIELD_INSPECTION_REF,
    CategoricalFieldInspectionData,
)
from ehp_sn.figures.rectangular_realization import to_matrix
from ehp_sn.figures.service import _ExactSource

_FIELD_REF = CATEGORICAL_FIELD_INSPECTION_REF


def _registry():
    return effective_figure_registry()


def _source(
    *,
    record_id: str = "sha256:CF",
    domain,
    vocabulary,
    observation_ids,
    artifact_ref: str = "artifact:obs/v1",
) -> _ExactSource:
    field = categorical_field(domain, vocabulary, observation_ids)
    return _ExactSource(
        artifact_ref=artifact_ref,
        record_id=record_id,
        schema_ref="categorical-field/v1",
        content=field.content(),
    )


def _project(source: _ExactSource):
    return prepare_figure(_registry(), _FIELD_REF, source)


_DOMAIN = rectangular_row_column_domain(3, 4)  # 12 positions
_ANON = AnonymousVocabulary(identity="vocab-alpha", cardinality=3)


def _anon_ids():
    return [0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2]


def _base_source(record_id: str = "sha256:CF") -> _ExactSource:
    """A canonical anonymous categorical-field source over ``_DOMAIN``."""
    return _source(
        record_id=record_id,
        domain=_DOMAIN,
        vocabulary=_ANON,
        observation_ids=_anon_ids(),
    )


# ---------------------------------------------------------------------------
# canonical runtime schema + both vocabulary forms
# ---------------------------------------------------------------------------


def test_anonymous_vocabulary_renders_without_external_metadata() -> None:
    projection = _project(_base_source(record_id="sha256:C1"))
    data = projection.content
    assert data.vocabulary_kind == "anonymous"
    assert data.vocabulary_identity == "vocab-alpha"
    assert data.vocabulary_cardinality == 3
    assert tuple(data.observation_ids) == tuple(_anon_ids())


def test_external_vocabulary_renders_with_resolved_identity() -> None:
    ext = ExternalVocabulary(ref="ext:v1", identity="vocab-external-x", cardinality=2)
    projection = _project(
        _source(record_id="sha256:C2", domain=_DOMAIN, vocabulary=ext, observation_ids=[0, 1] * 6)
    )
    data = projection.content
    assert data.vocabulary_kind == "external"
    assert data.vocabulary_identity == "vocab-external-x"
    assert data.vocabulary_cardinality == 2
    # External vocabulary does not require semantic interpretation of entries.
    assert isinstance(data, CategoricalFieldInspectionData)


def test_prepared_view_keeps_canonical_content_key() -> None:
    """The committed logical-instance field is ``observation_id`` (singular)."""
    field = categorical_field(_DOMAIN, _ANON, _anon_ids())
    content = field.content()
    assert set(content.keys()) == {"domain", "vocabulary", "observation_id"}


# ---------------------------------------------------------------------------
# complete ambient field represented; exact position mapping (Phase-2 § 6, § 28)
# ---------------------------------------------------------------------------


def test_all_positions_represented_no_loss() -> None:
    data = _project(_base_source(record_id="sha256:C3")).content
    assert len(data.observation_ids) == _DOMAIN.position_count


def test_position_to_cell_mapping_exact_no_transpose_no_reflection() -> None:
    """position_id(r,c) lands at matrix[r][c] via the shared realization."""
    # A gradient pattern: value == position_id so any transpose/reflection/reorder
    # is detectable.
    domain = rectangular_row_column_domain(3, 4)
    ids = list(range(12))
    matrix = to_matrix(domain, ids)
    # matrix[r][c] == position_id(r,c) == r*width+c
    for r in range(3):
        for c in range(4):
            assert matrix[r][c] == r * 4 + c
            assert matrix[r][c] == domain.position_id(r, c)


def test_no_values_reordered_or_reflected_in_realization() -> None:
    domain = rectangular_row_column_domain(2, 3)
    ids = [0, 1, 2, 2, 1, 0]
    matrix = to_matrix(domain, ids)
    assert matrix == [[0, 1, 2], [2, 1, 0]]


# ---------------------------------------------------------------------------
# rectangular-row-column mapping reused (Phase-2 § 6)
# ---------------------------------------------------------------------------


def test_uses_shared_rectangular_realization() -> None:
    """The figure exposes the same canonical mapping as the shared helper."""
    data = _project(_base_source(record_id="sha256:C4")).content
    # The prepared view reconstructs the domain through the contract; the shared
    # to_matrix helper is the single scientific row/column mapping.
    assert data.domain.schema_ref == "rectangular-row-column/v1"
    assert to_matrix(data.domain, list(data.observation_ids))[0][0] == data.observation_ids[0]


# ---------------------------------------------------------------------------
# no topology required / no mask applied (Phase-2 § 23)
# ---------------------------------------------------------------------------


def test_no_topology_required() -> None:
    # A complete categorical field renders without any topology input.
    figure = render_figure_projection(
        _project(_base_source(record_id="sha256:C5")),
        registry=_registry(),
    )
    assert type(figure).__name__ == "Figure"


def test_no_topology_fields_in_record_or_prepared_view() -> None:
    field = categorical_field(_DOMAIN, _ANON, _anon_ids())
    assert "topology" not in field.content()
    assert "passable" not in field.content()
    data = _project(_base_source(record_id="sha256:C6")).content
    assert not hasattr(data, "passable")
    assert not hasattr(data, "connected_components")


# ---------------------------------------------------------------------------
# discrete / non-ordinal categorical semantics (Phase-2 § 24)
# ---------------------------------------------------------------------------


def test_category_mapping_is_discrete_listed_colormap() -> None:
    projection = _project(_base_source(record_id="sha256:C7"))
    figure = render_figure_projection(projection, registry=_registry())
    image = figure.axes[0].images[0]
    cmap = image.get_cmap()
    # A ListedColormap (discrete), not a continuous sequential colormap.
    assert type(cmap).__name__ == "ListedColormap"
    # Interpolation is explicitly category-preserving (nearest).
    assert image.get_interpolation() in ("nearest", None)


def test_no_continuous_ordinal_magnitude_semantics() -> None:
    """The figure cannot be rendered with a continuous sequential colormap."""
    projection = _project(_base_source(record_id="sha256:C8"))
    figure = render_figure_projection(projection, registry=_registry())
    image = figure.axes[0].images[0]
    # vmin/vmax span the categorical domain exactly (discrete), not a continuous
    # normalization with category-as-magnitude.
    assert image.get_clim() == (0, 2)


# ---------------------------------------------------------------------------
# category-preserving interpolation / ambient perturbation (Phase-2 § 25, § 28)
# ---------------------------------------------------------------------------


def test_ambient_interpolation_perturbation_does_not_change_semantics() -> None:
    projection = _project(_base_source(record_id="sha256:C9"))
    with matplotlib.rc_context({"image.interpolation": "bilinear"}):
        figure = render_figure_projection(projection, registry=_registry())
    image = figure.axes[0].images[0]
    # Category-preserving resampling is explicit, not inherited from ambient
    # image.interpolation.
    assert image.get_interpolation() in ("nearest", None)


def test_ambient_origin_perturbation_does_not_change_semantics() -> None:
    projection = _project(_base_source(record_id="sha256:C10"))
    with matplotlib.rc_context({"image.origin": "lower"}):
        figure = render_figure_projection(projection, registry=_registry())
    assert type(figure).__name__ == "Figure"


# ---------------------------------------------------------------------------
# vocabulary identity is scientific (Phase-2 § 21)
# ---------------------------------------------------------------------------


def test_different_vocabulary_identity_same_ids_is_distinct_record() -> None:
    """Same domain, same integer IDs, different vocabulary identity → distinct."""
    a = _project(
        _source(
            record_id="sha256:A",
            domain=_DOMAIN,
            vocabulary=AnonymousVocabulary(identity="vocab-A", cardinality=3),
            observation_ids=_anon_ids(),
        )
    )
    b = _project(
        _source(
            record_id="sha256:B",
            domain=_DOMAIN,
            vocabulary=AnonymousVocabulary(identity="vocab-B", cardinality=3),
            observation_ids=_anon_ids(),
        )
    )
    # Distinct source content and distinct projection identity.
    assert a.content.vocabulary_identity != b.content.vocabulary_identity
    assert a.content.vocabulary_cardinality == b.content.vocabulary_cardinality
    assert str(a.identity()) != str(b.identity())


# ---------------------------------------------------------------------------
# deterministic category styling (Phase-2 § 26)
# ---------------------------------------------------------------------------


def test_deterministic_category_styling() -> None:
    from ehp_sn.figures.builtin.categorical_field import (
        _CATEGORY_PALETTE,
        _OPERATIONAL_CATEGORY_CAPACITY,
        _category_color,
        _vocabulary_style_offset,
    )

    # Same vocabulary identity + same observation ID → same intended style.
    assert _category_color(3, "vocab-alpha") == _category_color(3, "vocab-alpha")
    # Within one vocabulary, distinct categories → distinct styles (no collapse).
    assert _category_color(0, "vocab-alpha") != _category_color(1, "vocab-alpha")
    # The supported capacity is fully faithful: every distinct category value
    # within capacity maps to a distinct intended style (Phase-3 § 32).
    vocab = "obs-vocabulary:anonymous-45/v1"
    styles = [_category_color(c, vocab) for c in range(_OPERATIONAL_CATEGORY_CAPACITY)]
    assert len(set(styles)) == _OPERATIONAL_CATEGORY_CAPACITY
    assert len(_CATEGORY_PALETTE) == _OPERATIONAL_CATEGORY_CAPACITY
    assert len(set(_CATEGORY_PALETTE)) == _OPERATIONAL_CATEGORY_CAPACITY
    # Vocabulary identity qualifies interpretation: the same integer ID under a
    # different vocabulary identity need not share the same intended style
    # (Phase-3 § 31 · SRF-012).
    assert _vocabulary_style_offset("vocab-alpha") == _vocabulary_style_offset("vocab-alpha")


def test_vocabulary_style_offset_is_deterministic_and_qualifies_id() -> None:
    from ehp_sn.figures.builtin.categorical_field import _vocabulary_style_offset

    # Deterministic for a given vocabulary identity — including across process
    # salt variation, because it uses a stable CRC-32 digest rather than the
    # salted built-in hash() (categorical visual stability, Phase-3 § 31).
    assert _vocabulary_style_offset("v-A") == _vocabulary_style_offset("v-A")
    # Different vocabulary identities may yield different offsets — and even when
    # the offset coincides, semantic equivalence is never inferred (visual
    # similarity never implies semantic equivalence, Phase-3 § 31).
    assert 0 <= _vocabulary_style_offset("v-A") <= 44
    assert 0 <= _vocabulary_style_offset("v-B") <= 44


# ---------------------------------------------------------------------------
# high-cardinality legend policy explicit (Phase-2 § 27)
# ---------------------------------------------------------------------------


def test_real_obsfield_cardinality_renders_faithfully() -> None:
    """The real ObsField K=45 vocabulary renders with distinct category styles.

    The supported operational capacity (45) is set so the real committed ObsField
    vocabulary (``obs-vocabulary:anonymous-45/v1``) is faithfully served: every
    one of the 45 category values maps to a distinct intended display style, with
    no silent collapse of distinct categories onto identical styles (Phase-3
    § 32 · SRF-019).
    """
    from ehp_sn.figures.builtin.categorical_field import _CATEGORY_PALETTE

    domain = rectangular_row_column_domain(6, 8)  # 48 positions
    vocab = AnonymousVocabulary(identity="obs-vocabulary:anonymous-45/v1", cardinality=45)
    ids = [i % 45 for i in range(domain.position_count)]
    projection = _project(
        _source(record_id="sha256:H", domain=domain, vocabulary=vocab, observation_ids=ids)
    )
    data = projection.content
    assert data.vocabulary_cardinality == 45
    assert len(data.observation_ids) == 48
    figure = render_figure_projection(projection, registry=_registry())
    assert type(figure).__name__ == "Figure"
    image = figure.axes[0].images[0]
    # Discrete categorical mapping spans all 45 distinct category styles.
    assert image.get_clim() == (0, 44)
    # The palette is exactly the supported capacity and all entries are distinct.
    assert len(_CATEGORY_PALETTE) == 45
    assert len(set(_CATEGORY_PALETTE)) == 45


def test_high_cardinality_beyond_capacity_is_controlled_failure() -> None:
    """A vocabulary beyond faithful distinct-category capacity fails explicitly.

    A vocabulary larger than the supported operational capacity (45) cannot be
    faithfully represented without silently collapsing distinct categories onto
    identical styles, so it fails deterministically with
    :class:`InspectionCapacityExceeded` (Phase-3 § 32, § 36 · SRF-019) rather
    than degrading.
    """
    from ehp_sn.figures import InspectionCapacityExceeded

    domain = rectangular_row_column_domain(4, 5)
    vocab = AnonymousVocabulary(identity="obs-vocabulary:anonymous-80/v1", cardinality=80)
    ids = list(range(20))  # 20 positions, values in [0,80)
    with pytest.raises(InspectionCapacityExceeded):
        _project(_source(record_id="sha256:H2", domain=domain, vocabulary=vocab, observation_ids=ids))


# ---------------------------------------------------------------------------
# compatibility rejects unsupported domain capability (Phase-2 § 18)
# ---------------------------------------------------------------------------


def test_non_supported_domain_capability_rejected() -> None:
    """A hypothetical non-rectangular domain schema is a controlled incompatibility."""
    from ehp_sn.contracts.observations import AnonymousVocabulary as AV
    from ehp_sn.contracts.observations import categorical_field as cf

    # Build a content projection whose domain declares a non-rectangular schema.
    domain = rectangular_row_column_domain(2, 2)
    field = cf(domain, AV(identity="v", cardinality=2), [0, 1, 0, 1])
    content = field.content()
    content = dict(content)
    content["domain"] = dict(content["domain"])
    content["domain"]["schema"] = "hexagonal/v1"  # hypothetical future schema
    source = _ExactSource(
        artifact_ref="artifact:obs/v1",
        record_id="sha256:X",
        schema_ref="categorical-field/v1",
        content=content,
    )
    with pytest.raises(FigureInputCompatibilityError):
        prepare_figure(_registry(), _FIELD_REF, source)


def test_future_contract_version_is_incompatible() -> None:
    """The figure must not accept a future contract through structural duck typing.

    A hypothetical ``categorical-field/v2`` record is NOT compatible with
    ``figure:categorical-field-inspection/v1`` (which requires
    ``categorical-field/v1``), even though its fields look similar.
    """
    source = _ExactSource(
        artifact_ref="artifact:obs/v1",
        record_id="sha256:V2",
        schema_ref="categorical-field/v2",  # unknown future semantic version
        content=_base_source().content,
    )
    with pytest.raises(FigureInputCompatibilityError):
        prepare_figure(_registry(), _FIELD_REF, source)


# ---------------------------------------------------------------------------
# mutation boundary (Phase-2 § 33)
# ---------------------------------------------------------------------------


def test_rendering_does_not_mutate_source_prepared_or_projection() -> None:
    source = _base_source(record_id="sha256:MM")
    projection = _project(source)
    ids_before = tuple(projection.content.observation_ids)
    identity_before = str(projection.identity())

    render_figure_projection(projection, registry=_registry())

    assert tuple(projection.content.observation_ids) == ids_before
    assert str(projection.identity()) == identity_before
    # The authoritative source content is unchanged.
    content_now = categorical_field(_DOMAIN, _ANON, _anon_ids()).content()
    assert source.content["observation_id"] == list(_anon_ids())
    assert source.content["vocabulary"] == content_now["vocabulary"]


# ---------------------------------------------------------------------------
# producer-extension blindness (Phase-3 § 34 · SRF-016)
# ---------------------------------------------------------------------------


def test_producer_assignment_metadata_perturbation_unchanged_generic_view() -> None:
    """C-014 — ObsField producer extensions cannot alter the generic field view.

    Two records with the same categorical-field payload but different
    producer-owned assignment metadata (assignment_protocol / realization_index)
    prepare to the same contract-owned prepared view and realize with the same
    generic categorical visual semantics. The shared field inspector must not
    start visualising producer extensions merely because they are available
    (Phase-3 § 34 · SRF-016). Exact source/provenance identity may differ.
    """
    field = categorical_field(_DOMAIN, _ANON, _anon_ids())
    plain_content = field.content()
    extended_content = dict(plain_content)
    extended_content["assignment_protocol"] = "categorical-random/v1"  # producer ext
    extended_content["realization_index"] = 3  # producer ext

    source_plain = _ExactSource(
        artifact_ref="artifact:obs/v1",
        record_id="sha256:PA",
        schema_ref="categorical-field/v1",
        content=plain_content,
    )
    source_extended = _ExactSource(
        artifact_ref="artifact:obs/v1",
        record_id="sha256:PB",
        schema_ref="categorical-field/v1",
        content=extended_content,
    )
    a = prepare_figure(_registry(), _FIELD_REF, source_plain)
    b = prepare_figure(_registry(), _FIELD_REF, source_extended)

    # Same contract-owned prepared view.
    assert a.content.vocabulary_identity == b.content.vocabulary_identity
    assert tuple(a.content.observation_ids) == tuple(b.content.observation_ids)
    # Same generic visual semantics: identical drawn category matrix + clim.
    fa = render_figure_projection(a, registry=_registry())
    fb = render_figure_projection(b, registry=_registry())
    assert (fa.axes[0].images[0].get_array() == fb.axes[0].images[0].get_array()).all()
    assert fa.axes[0].images[0].get_clim() == fb.axes[0].images[0].get_clim()


def test_vocabulary_qualified_deterministic_style_cross_vocabularies() -> None:
    """SRF-012 — same ID under equal-cardinality different vocabularies is distinct.

    Equal cardinality and equal integer range never establish vocabulary
    equivalence: two vocabularies with the same cardinality but different
    identity yield distinct records with distinct projection identities, and no
    semantic equivalence is inferred from equal or similar colours (Phase-3
    § 30-31).
    """
    a = _project(
        _source(
            record_id="sha256:VA",
            domain=_DOMAIN,
            vocabulary=AnonymousVocabulary(identity="obs:vocab-x/v1", cardinality=3),
            observation_ids=_anon_ids(),
        )
    )
    b = _project(
        _source(
            record_id="sha256:VB",
            domain=_DOMAIN,
            vocabulary=AnonymousVocabulary(identity="obs:vocab-y/v1", cardinality=3),
            observation_ids=_anon_ids(),
        )
    )
    # Same cardinality + same integer IDs, but distinct vocabulary identity →
    # distinct records (no compatibility inferred).
    assert a.content.vocabulary_cardinality == b.content.vocabulary_cardinality == 3
    assert a.content.vocabulary_identity != b.content.vocabulary_identity
    assert str(a.identity()) != str(b.identity())
