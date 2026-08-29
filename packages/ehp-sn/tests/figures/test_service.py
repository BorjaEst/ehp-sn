"""Generic figure-service tests (Phase 1 bootstrap slice).

These test :mod:`ehp_sn.figures.service`: the generic figure orchestration —
resolving a requested figure through the ordinary component catalogue,
validating its semantic input requirement, preparing the projection, and
realizing a Matplotlib Figure.

They are headless: they select the non-interactive Matplotlib backend before
any pyplot use (Phase-1 § 16 · P1-T14, § 19.11).

They verify:

* 19.2 an unknown / non-figure / malformed figure reference is a controlled
  catalogue error with no fallback;
* 19.3 a contract mismatch is a controlled input-compatibility error before any
  rendering;
* 19.8 the figure layer consumes the parent-resolved source exactly once;
* 19.9 rendering does not mutate the authoritative source, prepared view, or
  projection;
* 19.11 the figure-service path succeeds under a non-interactive backend.

Integration over a real committed artifact lives at repository level in
``tests/integration/test_data_inspect_figure.py`` (root-level integration scope).
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless backend required for P1-19.11

import pytest
from ehp_sn.discovery import ComponentRegistry
from ehp_sn.figures import (
    FigureInputCompatibilityError,
    UnknownFigureError,
    effective_figure_registry,
    prepare_figure,
    render_figure_projection,
)
from ehp_sn.figures.projection import FigureProjection
from ehp_sn.figures.service import _ExactSource

#: A canonical raster-topology/v1 source used across unit-level tests.
_SOURCE = _ExactSource(
    artifact_ref="artifact:dg/v1",
    record_id="sha256:AAA",
    schema_ref="raster-topology/v1",
    content={
        "domain": {"height": 3, "width": 4, "position_count": 12},
        "passable": [True] * 12,
    },
)

_FIGURE_REF = "figure:raster-topology-inspection/v1"


def _registry() -> ComponentRegistry:
    return effective_figure_registry()


# ---------------------------------------------------------------------------
# 19.2 unknown figure → controlled catalogue/component error, no fallback
# ---------------------------------------------------------------------------


def test_unknown_figure_is_controlled_catalogue_error() -> None:
    with pytest.raises(UnknownFigureError):
        prepare_figure(_registry(), "figure:does-not-exist/v1", _SOURCE)


def test_non_figure_reference_is_controlled_error() -> None:
    # A substrate-shaped reference must not resolve as a figure.
    with pytest.raises(UnknownFigureError):
        prepare_figure(_registry(), "substrate:dagflow/v1", _SOURCE)


def test_malformed_figure_reference_is_controlled_error() -> None:
    with pytest.raises(UnknownFigureError):
        prepare_figure(_registry(), "not a reference", _SOURCE)


# ---------------------------------------------------------------------------
# 19.3 contract mismatch → controlled input-compatibility error before rendering
# ---------------------------------------------------------------------------


def test_incompatible_logical_contract_fails_before_rendering() -> None:
    source = _ExactSource(
        artifact_ref="artifact:dg/v1",
        record_id="sha256:CCC",
        schema_ref="simple-digraph/v1",
        content={"node_count": 1},
    )
    # The failure surfaces as a controlled input-compatibility error during
    # preparation (before any Matplotlib rendering), never a shape/imshow error.
    with pytest.raises(FigureInputCompatibilityError):
        prepare_figure(_registry(), _FIGURE_REF, source)


# ---------------------------------------------------------------------------
# 19.8 no double record selection
# ---------------------------------------------------------------------------


def test_figure_layer_consumes_exact_resolved_source_no_reselection() -> None:
    projection = prepare_figure(_registry(), _FIGURE_REF, _SOURCE)
    # The projection carries exactly the source the parent supplied; there is
    # no figure-side record selection identity beyond it (Phase-1 § 10 · P1-T8).
    assert projection.source.record_id == _SOURCE.record_id
    assert projection.source.artifact_ref == _SOURCE.artifact_ref


# ---------------------------------------------------------------------------
# 19.9 rendering does not mutate authoritative source / prepared view / projection
# ---------------------------------------------------------------------------


def test_rendering_does_not_mutate_source_or_projection() -> None:
    source_content_before = {
        "domain": {"height": 3, "width": 4, "position_count": 12},
        "passable": [True] * 12,
    }
    source = _ExactSource(
        artifact_ref="artifact:dg/v1",
        record_id="sha256:DDD",
        schema_ref="raster-topology/v1",
        content=source_content_before,
    )
    projection = prepare_figure(_registry(), _FIGURE_REF, source)
    prepared_before = tuple(projection.source.content.passable)
    identity_before = str(projection.identity())

    render_figure_projection(projection, registry=_registry())

    assert tuple(projection.source.content.passable) == prepared_before
    assert str(projection.identity()) == identity_before
    # The authoritative source content dict is also untouched.
    assert source.content["passable"] == [True] * 12


# ---------------------------------------------------------------------------
# 19.11 headless realization
# ---------------------------------------------------------------------------


def test_headless_realization_produces_matplotlib_figure() -> None:
    projection = prepare_figure(_registry(), _FIGURE_REF, _SOURCE)
    figure = render_figure_projection(projection, registry=_registry())
    assert type(figure).__name__ == "Figure"
    # Exactly one Axes and one raster representation (Phase-1 § 13 · P1-T11).
    assert len(figure.axes) == 1


# ---------------------------------------------------------------------------
# 19.1 integration over a real committed raster record lives in
# ``tests/integration/test_data_inspect_figure.py`` (root-level integration
# scope, alongside the CLI-level figure integration tests).
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Generic orchestration API shape (P1-T10 / P1-T14)
# ---------------------------------------------------------------------------


def test_prepare_and_render_are_separate_stages() -> None:
    """The generic service separates projection creation from realization.

    ``prepare_figure`` returns a ``FigureProjection`` with no GUI/backend and
    no rendering side effects; ``render_figure_projection`` realizes it. This
    keeps scientific-view semantics independent of presentation (P1-T10).
    """
    projection = prepare_figure(_registry(), _FIGURE_REF, _SOURCE)
    assert isinstance(projection, FigureProjection)
    assert not hasattr(projection, "figure")  # projection is not a rendered figure
