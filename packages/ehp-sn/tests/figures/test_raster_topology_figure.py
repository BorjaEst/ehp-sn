"""Framework-owned raster-topology figure tests (Phase 1 bootstrap slice).

These test :mod:`ehp_sn.figures.builtin.raster_topology` — the first
framework-owned built-in figure (``figure:raster-topology-inspection/v1``),
whose complete scientific/structural meaning is expressible purely through the
framework-owned ``raster-topology/v1`` logical contract (Phase-1 § 6 · P1-T4).

They verify:

* 19.4 producer independence — equivalent raster-topology/v1 records from
  different contexts require no semantic modification and no producer branch;
* preparation reconstructs the stable typed topology view without deriving new
  scientific conclusions (P1-T9);
* direct Matplotlib realization — one Figure, one Axes, one raster/image
  representation (P1-T11/P1-T12);
* 19.10 controlled presentation isolation — explicit Phase-1 presentation wins
  over perturbed ambient Matplotlib state (P1-T13).

These tests select the headless backend before any pyplot use.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless backend required for P1-19.10/19.11

from ehp_sn.figures import (
    effective_figure_registry,
    prepare_figure,
    render_figure_projection,
)
from ehp_sn.figures.service import _ExactSource

_FIGURE_REF = "figure:raster-topology-inspection/v1"


def _registry():
    return effective_figure_registry()


def _source(
    *,
    artifact_ref: str = "artifact:dg/v1",
    record_id: str,
    passable: list[bool],
) -> _ExactSource:
    return _ExactSource(
        artifact_ref=artifact_ref,
        record_id=record_id,
        schema_ref="raster-topology/v1",
        content={
            "extent": {"height": 3, "width": 4, "position_count": 12},
            "passable": passable,
        },
    )


def _project(source: _ExactSource):
    return prepare_figure(_registry(), _FIGURE_REF, source)


# ---------------------------------------------------------------------------
# 19.4 producer independence — equivalent raster records, no producer branch
# ---------------------------------------------------------------------------


def test_equivalent_records_use_same_figure_no_producer_branch() -> None:
    # Two raster-topology/v1 records from different artifact/producer contexts
    # resolve through the identical FigureSpec with no producer-identity input.
    source_a = _source(artifact_ref="artifact:dg/v1", record_id="sha256:A1", passable=[True] * 12)
    source_b = _source(artifact_ref="artifact:fixture/v9", record_id="sha256:B2", passable=[True] * 12)
    registry = _registry()
    # Neither source carries a producer identity; both prepare through the same
    # catalogue-resolved FigureSpec and both realize successfully.
    proj_a = prepare_figure(registry, _FIGURE_REF, source_a)
    proj_b = prepare_figure(registry, _FIGURE_REF, source_b)
    assert proj_a.figure_ref == proj_b.figure_ref == _FIGURE_REF
    assert proj_a.source.role == proj_b.source.role == "topology"
    assert render_figure_projection(proj_b, registry=registry) is not None


# ---------------------------------------------------------------------------
# P1-T9 preparation reconstructs the stable typed topology view
# ---------------------------------------------------------------------------


def test_prepare_reconstructs_typed_raster_topology() -> None:
    projection = _project(_source(record_id="sha256:AAA", passable=[True] * 12))
    content = projection.source.content
    assert content.__class__.__name__ == "RasterTopology"
    assert content.schema_ref == "raster-topology/v1"
    assert content.extent.height == 3
    assert content.extent.width == 4
    assert content.extent.position_count == 12
    assert tuple(content.passable) == (True,) * 12


def test_prepare_uses_authoritative_passability() -> None:
    passable = [True, True, False] + [True] * 9
    projection = _project(_source(record_id="sha256:AAA", passable=passable))
    assert tuple(projection.source.content.passable) == tuple(passable)


# ---------------------------------------------------------------------------
# P1-T11/P1-T12 direct Matplotlib realization — one Figure, one Axes
# ---------------------------------------------------------------------------


def test_realization_uses_one_figure_one_axes() -> None:
    projection = _project(_source(record_id="sha256:AAA", passable=[True] * 12))
    figure = render_figure_projection(projection, registry=_registry())
    assert type(figure).__name__ == "Figure"
    assert len(figure.axes) == 1
    # One visualized image (imshow) carries the passability.
    axes = figure.axes[0]
    images = axes.images
    assert len(images) == 1


def test_realization_annotates_axes() -> None:
    projection = _project(_source(record_id="sha256:AAA", passable=[True] * 12))
    figure = render_figure_projection(projection, registry=_registry())
    axes = figure.axes[0]
    assert axes.get_xlabel() == "column"
    assert axes.get_ylabel() == "row"
    assert axes.get_title() != ""


# ---------------------------------------------------------------------------
# 19.10 ambient Matplotlib-state perturbation → explicit Phase-1 presentation
# ---------------------------------------------------------------------------


def test_explicit_presentation_beats_perturbed_ambient_state() -> None:
    projection = _project(_source(record_id="sha256:AAA", passable=[True] * 12))
    # Under a perturbed ambient style the figure must still use its explicit
    # Phase-1 presentation (6×6 inches) via its controlled rc defaults.
    with matplotlib.rc_context({"figure.figsize": (1, 1), "font.size": 6}):
        figure = render_figure_projection(projection, registry=_registry())
    width, height = figure.get_size_inches()
    assert (round(width), round(height)) == (6, 6)
