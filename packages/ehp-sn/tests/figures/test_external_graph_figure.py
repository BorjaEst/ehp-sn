"""Externally contributed companion figure tests (Phase 2).

These test the **externally contributed** test-only companion figures from the
independently installed ``test-figure-provider`` distribution through the
``ehp_sn.figures.providers`` entry-point group:

* ``figure:digraph-summary/v1`` — compatible with ``simple-digraph/v1``;
* ``figure:field-summary/v1`` — compatible with ``categorical-field/v1``.

The framework-owned record inspectors (``figure:simple-digraph-inspection/v1``,
``figure:categorical-field-inspection/v1``) are built-in figures in ``ehp_sn``;
this file does **not** re-test those as external. It verifies (Phase-2 § 39-40):

* the external companions resolve through the same ordinary component catalogue
  as the built-in figures (P2-A/P2-C) — origin is irrelevant to normal
  resolution;
* they render their contract record through the same service path;
* they make ``--figure auto`` over their record **ambiguous** with the built-in
  inspector (Phase-2 § 37, § 40);
* ``--list-figures`` returns both the built-in and external compatible figures;
* the graph figure is not present in a plain registry without the installed
  provider (no second authoritative registry).

These require the fixture distribution to be installed. If it is absent they
skip, mirroring the existing research-provider integration test pattern.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless backend required

import pytest
from ehp_sn.figures import (
    AmbiguousFigureError,
    FigureInputCompatibilityError,
    effective_figure_registry,
    list_compatible_figures,
    prepare_figure,
    render_figure_projection,
    resolve_auto_figure,
)
from ehp_sn.figures.service import _ExactSource

try:
    import test_figure_provider  # noqa: F401
except ImportError:  # pragma: no cover - fixture distribution not installed
    test_figure_provider = None  # type: ignore[assignment]

_GRAPH_COMPANION = "figure:digraph-summary/v1"
_FIELD_COMPANION = "figure:field-summary/v1"
_GRAPH_REF = "figure:simple-digraph-inspection/v1"
_RASTER_REF = "figure:raster-topology-inspection/v1"
_FIELD_REF = "figure:categorical-field-inspection/v1"

REQUIRES_PROVIDER = pytest.mark.skipif(
    test_figure_provider is None,
    reason="test-figure-provider fixture distribution is not installed",
)


def _graph_source(*, record_id: str = "sha256:BBB", edges=None, node_count: int = 4) -> _ExactSource:
    return _ExactSource(
        artifact_ref="artifact:dag/v1",
        record_id=record_id,
        schema_ref="simple-digraph/v1",
        content={
            "node_count": node_count,
            "edges": edges if edges is not None else [(0, 1), (1, 2), (2, 3)],
        },
    )


def _raster_source() -> _ExactSource:
    return _ExactSource(
        artifact_ref="artifact:dg/v1",
        record_id="sha256:ZZZ",
        schema_ref="raster-topology/v1",
        content={
            "extent": {"height": 3, "width": 4, "position_count": 12},
            "passable": [True] * 12,
        },
    )


# ---------------------------------------------------------------------------
# P2-A / P2-C — external companions resolve through the ordinary catalogue
# ---------------------------------------------------------------------------


@REQUIRES_PROVIDER
def test_external_companion_figures_resolve_through_ordinary_catalogue() -> None:
    registry = effective_figure_registry()
    assert registry.resolve(_GRAPH_COMPANION).kind == "figure"
    assert registry.resolve(_FIELD_COMPANION).kind == "figure"


@REQUIRES_PROVIDER
def test_builtin_and_external_figures_share_one_catalogue() -> None:
    """Built-in inspectors and external companions enter the same catalogue."""
    registry = effective_figure_registry()
    refs = sorted(d.ref.canonical for d in registry.iter(kind="figure"))
    assert _GRAPH_REF in refs
    assert _RASTER_REF in refs
    assert _GRAPH_COMPANION in refs
    assert _FIELD_COMPANION in refs


# ---------------------------------------------------------------------------
# the external companions render through the same service path
# ---------------------------------------------------------------------------


@REQUIRES_PROVIDER
def test_digraph_summary_renders_graph_record() -> None:
    registry = effective_figure_registry()
    projection = prepare_figure(registry, _GRAPH_COMPANION, _graph_source())
    assert projection.figure_ref == _GRAPH_COMPANION
    figure = render_figure_projection(projection, registry=registry)
    assert type(figure).__name__ == "Figure"


@REQUIRES_PROVIDER
def test_field_summary_renders_field_record() -> None:
    from ehp_sn.contracts.domains import rectangular_row_column_domain
    from ehp_sn.contracts.observations import AnonymousVocabulary, categorical_field

    domain = rectangular_row_column_domain(2, 3)
    vocab = AnonymousVocabulary(identity="v", cardinality=2)
    field = categorical_field(domain, vocab, [0, 1, 0, 1, 0, 1])
    source = _ExactSource(
        artifact_ref="artifact:obs/v1",
        record_id="sha256:FS",
        schema_ref="categorical-field/v1",
        content=field.content(),
    )
    registry = effective_figure_registry()
    projection = prepare_figure(registry, _FIELD_COMPANION, source)
    assert projection.figure_ref == _FIELD_COMPANION
    figure = render_figure_projection(projection, registry=registry)
    assert type(figure).__name__ == "Figure"


# ---------------------------------------------------------------------------
# Phase-2 § 40 — a test-only compatible figure creates ambiguity for --figure auto
# ---------------------------------------------------------------------------


@REQUIRES_PROVIDER
def test_auto_is_ambiguous_when_external_compatible_figure_present() -> None:
    """Built-in graph inspector + external digraph-summary both match → ambiguous."""
    registry = effective_figure_registry()
    compatible = list_compatible_figures(registry, _graph_source())
    refs = sorted(s.ref.canonical for s in compatible)
    assert _GRAPH_REF in refs
    assert _GRAPH_COMPANION in refs
    with pytest.raises(AmbiguousFigureError):
        resolve_auto_figure(registry, _graph_source())


@REQUIRES_PROVIDER
def test_auto_is_ambiguous_for_categorical_when_external_compatible_present() -> None:
    from ehp_sn.contracts.domains import rectangular_row_column_domain
    from ehp_sn.contracts.observations import AnonymousVocabulary, categorical_field

    domain = rectangular_row_column_domain(2, 2)
    vocab = AnonymousVocabulary(identity="v", cardinality=2)
    field = categorical_field(domain, vocab, [0, 1, 0, 1])
    source = _ExactSource(
        artifact_ref="artifact:obs/v1",
        record_id="sha256:CAM",
        schema_ref="categorical-field/v1",
        content=field.content(),
    )
    registry = effective_figure_registry()
    compatible = list_compatible_figures(registry, source)
    refs = sorted(s.ref.canonical for s in compatible)
    assert _FIELD_REF in refs
    assert _FIELD_COMPANION in refs
    with pytest.raises(AmbiguousFigureError):
        resolve_auto_figure(registry, source)


@REQUIRES_PROVIDER
def test_explicit_exact_ref_still_selects_deterministically() -> None:
    """An explicit canonical ref resolves deterministically despite ambiguity."""
    registry = effective_figure_registry()
    projection = prepare_figure(registry, _GRAPH_REF, _graph_source())
    assert projection.figure_ref == _GRAPH_REF


# ---------------------------------------------------------------------------
# explicit selection mandatory; no silent substitution (negative tests)
# ---------------------------------------------------------------------------


@REQUIRES_PROVIDER
def test_graph_figure_against_raster_record_is_controlled_mismatch() -> None:
    with pytest.raises(FigureInputCompatibilityError):
        prepare_figure(effective_figure_registry(), _GRAPH_REF, _raster_source())


@REQUIRES_PROVIDER
def test_companion_against_wrong_contract_is_controlled_mismatch() -> None:
    with pytest.raises(FigureInputCompatibilityError):
        prepare_figure(effective_figure_registry(), _GRAPH_COMPANION, _raster_source())


# ---------------------------------------------------------------------------
# P2-14 — the graph figure is not present in a plain registry without provider
# ---------------------------------------------------------------------------


@REQUIRES_PROVIDER
def test_graph_figure_not_present_in_plain_registry_without_provider() -> None:
    """A bare registry without the built-in/installed providers has no graph figure.

    There is no second authoritative registry that can re-resolve a figure whose
    provider is absent (Phase-1 § 19.12 analogue).
    """
    from ehp_sn.discovery import ComponentRegistry, UnknownReferenceError
    from ehp_sn.experiments import ComponentRef

    with pytest.raises(UnknownReferenceError):
        ComponentRegistry().resolve(ComponentRef.parse(_GRAPH_REF))
