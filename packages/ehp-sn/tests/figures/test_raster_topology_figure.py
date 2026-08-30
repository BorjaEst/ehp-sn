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

from typing import Any

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
    height: int = 3,
    width: int = 4,
    passable: list[bool],
) -> _ExactSource:
    return _ExactSource(
        artifact_ref=artifact_ref,
        record_id=record_id,
        schema_ref="raster-topology/v1",
        content={
            "extent": {"height": height, "width": width, "position_count": height * width},
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


# ---------------------------------------------------------------------------
# Phase-3 raster contract fixture matrix (§ 43, R-001..R-016)
# ---------------------------------------------------------------------------


def _rendered_grid(passable: list[bool], *, height: int = 3, width: int = 4) -> Any:
    """Prepare + realize a raster topology and return the drawn matrix values."""
    projection = _project(_source(record_id="sha256:RT", height=height, width=width, passable=passable))
    figure = render_figure_projection(projection, registry=_registry())
    image = figure.axes[0].images[0]
    return image.get_array()


def test_r1_smallest_legal_topology_1x1() -> None:
    """R-001 — a 1×1 passable topology renders as a single passable cell."""
    grid = _rendered_grid([True], height=1, width=1)
    assert grid.shape == (1, 1)
    assert grid[0, 0] == 1


def test_r2_one_row_many_columns() -> None:
    """R-002 — 1×N shape (detects assumptions about two-dimensional extent)."""
    passable = [True, False, True, False, True]
    grid = _rendered_grid(passable, height=1, width=5)
    assert grid.shape == (1, 5)
    assert list(grid[0]) == [1, 0, 1, 0, 1]


def test_r3_many_rows_one_column() -> None:
    """R-003 — N×1 shape complements R-002 and detects row/column swap."""
    passable = [True, False, True, False]
    grid = _rendered_grid(passable, height=4, width=1)
    assert grid.shape == (4, 1)
    assert [grid[r, 0] for r in range(4)] == [1, 0, 1, 0]


def test_r4_asymmetric_non_square_orientation_fixture() -> None:
    """R-004 — the asymmetric 2×3 orientation fixture (A . B / . C .).

    ``position_id(r, c) = r * width + c`` with the shared ``to_matrix`` mapping,
    so the drawn grid row 0 is the canonical first row (A,B) and row 1 the
    second (C centred). Any transpose or vertical/horizontal reflection changes
    the drawn placement and is detected here (Phase-3 § 21 · SRF-009).
    """
    # Positions: A(0,0), B(0,2), C(1,1) passable; others blocked.
    passable = [True, False, True, False, True, False]
    grid = _rendered_grid(passable, height=2, width=3)
    assert grid.shape == (2, 3)
    # Matrix row 0 == canonical row 0: A and B at columns 0 and 2.
    assert grid[0, 0] == 1  # A → (0,0)
    assert grid[0, 2] == 1  # B → (0,2)
    assert grid[0, 1] == 0  # (0,1) blocked
    # Matrix row 1 == canonical row 1: C at the centre column.
    assert grid[1, 1] == 1  # C → (1,1)
    assert grid[1, 0] == 0 and grid[1, 2] == 0


def test_r5_connected_irregular_topology() -> None:
    """R-005 — an irregular connected topology renders completely."""
    passable = [True, True, False, True, True, True]
    grid = _rendered_grid(passable, height=2, width=3)
    assert grid.shape == (2, 3)
    assert list(grid.ravel()) == [1, 1, 0, 1, 1, 1]


def test_r6_disconnected_topology_is_supported() -> None:
    """R-006 — the shared contract permits component_count > 1 / connected False.

    Even though DungeonGen-style producers normally emit connected topologies,
    the generic inspector accepts a disconnected one (Phase-3 § 22 · R-006).
    """
    # Top-left and bottom-right passable, separated by blockers → two components.
    passable = [True, False, False, False, False, True]
    projection = _project(_source(record_id="sha256:R6", passable=passable, width=3, height=2))
    topo = projection.source.content
    assert topo.component_count == 2
    assert topo.connected is False
    figure = render_figure_projection(projection, registry=_registry())
    assert type(figure).__name__ == "Figure"


def test_r7_canonical_extent_and_passable_consumed() -> None:
    """R-007 — prepare reads exactly the authoritative extent/passable fields."""
    passable = [True, False, True, False, True, True, False, True, False, False, True, True]
    projection = _project(_source(record_id="sha256:R7", passable=passable, height=3, width=4))
    topo = projection.source.content
    assert topo.extent.height == 3
    assert topo.extent.width == 4
    assert tuple(topo.passable) == tuple(passable)


def test_r8_three_point_orientation_mapping() -> None:
    """R-008 — canonical row-major placement verified for three points (SRF-009)."""
    # Positions 0, 5, 9 for a 3x4 grid: (0,0), (1,1), (2,1).
    passable = [False] * 12
    passable[0] = True
    passable[5] = True
    passable[9] = True
    grid = _rendered_grid(passable, height=3, width=4)
    assert grid[0, 0] == 1
    assert grid[1, 1] == 1
    assert grid[2, 1] == 1
    # All other cells blocked.
    assert int(grid[0, 3]) == 0
    assert int(grid[2, 3]) == 0


def test_r9_ambient_image_origin_perturbation_unchanged_semantics() -> None:
    """R-009 — ambient ``image.origin`` must not change scientific orientation.

    The raster sets an explicit origin; perturbing the ambient default must not
    transpose/reflect the drawn passability (Phase-3 § 21 · SRF-009).
    """
    passable = [True, False, True, False, True, False]  # 2x3 asymmetric
    with matplotlib.rc_context({"image.origin": "lower"}):
        grid_lower = _rendered_grid(passable, height=2, width=3)
    with matplotlib.rc_context({"image.origin": "upper"}):
        grid_upper = _rendered_grid(passable, height=2, width=3)
    # The semantic orientation is fixed by the figure, independent of ambient.
    assert (grid_lower == grid_upper).all()
    assert int(grid_lower[0, 0]) == 1  # canonical (0,0) at top-left regardless


def test_r10_transpose_and_reflection_detected() -> None:
    """R-010 — the drawn orientation detects transpose/reflection errors.

    Using the three-point orientation fixture, the drawn matrix must equal the
    canonical ``to_matrix`` result; any transpose/reflection would move A/B/C
    and fail these assertions (Phase-3 § 21).
    """
    from ehp_sn.contracts.domains import rectangular_row_column_domain
    from ehp_sn.figures.rectangular_realization import to_matrix

    passable = [True, False, True, False, True, False]
    grid = _rendered_grid(passable, height=2, width=3)
    expected = to_matrix(rectangular_row_column_domain(2, 3), [1 if p else 0 for p in passable])
    assert grid.tolist() == expected


def test_r11_canonical_state_count() -> None:
    """R-011 — state_count is the authoritative passable position count."""
    passable = [True, True, False, True, False, True, True, False]
    projection = _project(_source(record_id="sha256:R11", passable=passable, height=2, width=4))
    topo = projection.source.content
    assert topo.state_count == sum(passable)
    from ehp_sn.contracts.domains import rectangular_row_column_domain
    from ehp_sn.contracts.topology import raster_topology

    canonical = raster_topology(rectangular_row_column_domain(2, 4), passable)
    assert topo.state_count == canonical.state_count


def test_r12_canonical_connected_and_component_count() -> None:
    """R-012 — connected / component_count are the canonical contract views."""
    from ehp_sn.contracts.domains import rectangular_row_column_domain
    from ehp_sn.contracts.topology import raster_topology

    # One connected component (all passable).
    connected = [True] * 6
    projection = _project(_source(record_id="sha256:R12a", passable=connected, height=2, width=3))
    topo = projection.source.content
    canonical = raster_topology(rectangular_row_column_domain(2, 3), connected)
    assert topo.connected == canonical.connected is True
    assert topo.component_count == canonical.component_count == 1
    # Two components.
    disconnected = [True, False, False, False, False, True]
    projection = _project(_source(record_id="sha256:R12b", passable=disconnected, height=2, width=3))
    topo = projection.source.content
    canonical = raster_topology(rectangular_row_column_domain(2, 3), disconnected)
    assert topo.connected == canonical.connected is False
    assert topo.component_count == canonical.component_count == 2


def test_r13_component_visualization_creates_no_persistent_semantics() -> None:
    """R-013 — no persistent component IDs/ranking are exposed by the figure.

    ``component_count`` is contract-owned, but persistent component IDs are not.
    The figure must not invent persistent component semantics (Phase-3 § 23).
    """
    disconnected = [True, False, False, False, False, True]
    projection = _project(_source(record_id="sha256:R13", passable=disconnected, height=2, width=3))
    topo = projection.source.content
    # The prepared view exposes no persistent component-ID field.
    assert not hasattr(topo, "component_ids")
    assert not hasattr(topo, "component_labels")
    # Rendering produces exactly one image (no component-legend/channel).
    figure = render_figure_projection(projection, registry=_registry())
    assert len(figure.axes[0].images) == 1


def test_r14_producer_extension_perturbation_unchanged_generic_view() -> None:
    """R-014 — a producer extension outside the shared contract cannot alter the view.

    Two records with identical extent/passable but different/additional
    DungeonGen-style producer metadata (here a ``region_id`` extension) prepare
    to the same contract-owned prepared view and same generic visual semantics
    (producer-extension blindness · Phase-3 § 25 · SRF-016). Exact source
    identity/provenance may differ.
    """
    base = {"height": 2, "width": 3, "position_count": 6}
    passable = [True, False, True, False, True, False]
    source_plain = _ExactSource(
        artifact_ref="artifact:dg/v1",
        record_id="sha256:PA",
        schema_ref="raster-topology/v1",
        content={"extent": base, "passable": passable},
    )
    source_extended = _ExactSource(
        artifact_ref="artifact:dg/v1",
        record_id="sha256:PB",
        schema_ref="raster-topology/v1",
        content={"extent": base, "passable": passable, "region_id": 7},  # producer extension
    )
    a = prepare_figure(_registry(), _FIGURE_REF, source_plain)
    b = prepare_figure(_registry(), _FIGURE_REF, source_extended)
    # Same contract-owned prepared view (passability identical).
    assert tuple(a.source.content.passable) == tuple(b.source.content.passable)
    assert a.source.content.extent.height == b.source.content.extent.height
    # Same generic visual semantics: identical drawn passability grid.
    fa = render_figure_projection(a, registry=_registry())
    fb = render_figure_projection(b, registry=_registry())
    assert (fa.axes[0].images[0].get_array() == fb.axes[0].images[0].get_array()).all()


def test_r16_rendering_does_not_mutate_source_or_projection() -> None:
    """R-016 — inspection never mutates the committed source or projection data."""
    passable = [True, False, True, True, False, True]
    source = _ExactSource(
        artifact_ref="artifact:dg/v1",
        record_id="sha256:R16",
        schema_ref="raster-topology/v1",
        content={
            "extent": {"height": 2, "width": 3, "position_count": 6},
            "passable": passable,
        },
    )
    projection = _project(source)
    identity_before = str(projection.identity())
    prepared_before = tuple(projection.source.content.passable)

    figure = render_figure_projection(projection, registry=_registry())
    assert type(figure).__name__ == "Figure"

    assert tuple(projection.source.content.passable) == prepared_before
    assert str(projection.identity()) == identity_before
    assert source.content["passable"] == passable
    assert source.content["extent"] == {"height": 2, "width": 3, "position_count": 6}
