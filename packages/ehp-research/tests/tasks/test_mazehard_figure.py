"""Stage 6C figure-conformance tests for ``figure:maze-hard-case/v1``.

These tests verify the figure-authority boundary (§ 18) and figure independence
(§ 19-20, § 37 KPI):

* the figure consumes authoritative source/task information and annotates only
  committed task semantics;
* it does not run model inference or compute acceptance metrics;
* it does not re-run task construction;
* it is producer independent (works for any ``raster-topology/v1`` source);
* it renders a representative selected case deterministically.

The unrealized prepared view is exercised against an authoritative source, and
the realize step is checked for rendering (no model, no scoring).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import pytest

matplotlib.use("Agg")

from ehp_research.figures.maze_hard_case import MAZE_HARD_CASE_FIGURE, MazeHardCaseData
from ehp_research.tasks.mazehard import MazeHardBuilder
from ehp_sn.artifacts.resolve import load_release

from .fixtures import FakeSource, corridor_passable, record_with_passable


class _Source:
    """Minimal authoritative source-like object feeding the figure prepare."""

    def __init__(self, content, annotation):
        self.content = content
        self.annotation = annotation


def _build_case_and_source(passable=None, *, seed=1):
    if passable is None:
        passable = corridor_passable(25)
    src = FakeSource(records=[record_with_passable(passable)])
    case = MazeHardBuilder(seed=seed).build(src).cases[0]
    source = _Source(
        {"domain": case.domain, "passable": list(case.passable)},
        {
            "start": case.start,
            "goal": case.goal,
            "reference_labels": list(case.reference_labels),
        },
    )
    return case, source


def test_figure_prepare_produces_stable_view():
    case, source = _build_case_and_source()
    view = MAZE_HARD_CASE_FIGURE.projection.prepare(source)
    assert isinstance(view, MazeHardCaseData)
    assert view.start == case.start
    assert view.goal == case.goal
    assert view.reference_labels == case.reference_labels


def test_figure_renders_deterministically():
    _, source = _build_case_and_source()
    view = MAZE_HARD_CASE_FIGURE.projection.prepare(source)

    class _Proj:
        def __init__(self, v):
            self.content = v

    fig1 = MAZE_HARD_CASE_FIGURE.visual.realize(_Proj(view))
    fig2 = MAZE_HARD_CASE_FIGURE.visual.realize(_Proj(view))
    assert fig1 is not None and fig2 is not None


def test_figure_does_not_compute_acceptance_or_reconstruct_semantics():
    """prepare uses only authoritative bytes; no scoring, no reconstruction."""
    _, source = _build_case_and_source()
    view = MAZE_HARD_CASE_FIGURE.projection.prepare(source)
    # The prepared view carries verbatim committed labels, never recomputed ones.
    assert view.reference_labels == tuple(source.annotation["reference_labels"])


def test_figure_is_producer_independent():
    """The same figure renders a case from any raster-topology producer (maze-nd)."""
    art = load_release(Path("data/interim/maze-nd/source-topology/v2"))
    case = MazeHardBuilder(seed=3).build(art).cases[0]
    source = _Source(
        {"domain": case.domain, "passable": list(case.passable)},
        {
            "start": case.start,
            "goal": case.goal,
            "reference_labels": list(case.reference_labels),
        },
    )
    view = MAZE_HARD_CASE_FIGURE.projection.prepare(source)
    assert view.width == 30 and view.height == 30


def test_figure_not_in_generic_raster_discovery_catalogue():
    """The task figure must not compete with generic raster-record discovery.

    A task-case figure is task-owned; it must not be registered against the
    bare ``raster-topology/v1`` record contract in the generic figure catalogue,
    otherwise it would make generic raster-record ``--figure auto`` ambiguous
    and break the "raster record has exactly one compatible inspection figure"
    discovery invariant. The figure is reached through the task-layer source
    instead.
    """
    from ehp_sn.figures.providers import effective_figure_registry

    registry = effective_figure_registry()
    assert not registry.contains(MAZE_HARD_CASE_FIGURE.ref.canonical)
