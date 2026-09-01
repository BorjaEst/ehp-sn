"""Research-owned MazeHard task-case figure (Stage 6C).

``figure:maze-hard-case/v1`` explains one canonical MazeHard task case to a
domain expert without observing model behavior (Stage 6C § 17). It shows:

* source/problem structure — the maze over natural-domain positions;
* task-visible information — start and goal flags;
* authoritative target — the committed reference route / path-labelled target.

The figure's authoritative input is one ``raster-topology/v1`` source record
(the maze structure it can resolve) plus the committed task-case annotation
(start/goal/reference target) supplied through the figure source. It does **not**
re-run task construction, recompute acceptance, infer missing task semantics, or
perform model inference (Stage 6C § 18; ``FIG-002``). All annotating labels come
from the committed task representation — never reconstructed by this figure.

``prepare`` builds a stable prepared view from the authoritative source and the
supplied task-case annotation; ``realize`` renders it with Matplotlib. This is
a task-layer figure reached outside the generic raster discovery catalogue: it
is deliberately not registered in ``_RESEARCH_FIGURES`` and does not appear in
``effective_figure_registry()`` (see ``test_mazehard_figure.py``). It is
invoked directly by the MazeHard inspection path and introduces no parallel
task-figure registry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

from ehp_sn.contracts.topology import SCHEMA_REF as RASTER_TOPOLOGY_SCHEMA_REF
from ehp_sn.experiments import ComponentRef
from ehp_sn.figures.contracts import (
    FIGURE_KIND,
    FigureInputRequirement,
    FigureSpec,
    _DefaultsPartition,
    _ProjectionPartition,
    _VisualPartition,
)
from ehp_sn.figures.scope import SCOPE_RECORD

from ..tasks.mazehard.record import FREE, GOAL, PATH, START, WALL

#: The canonical reference of the MazeHard task-case figure.
MAZE_HARD_CASE_REF = "figure:maze-hard-case/v1"

_PROJECTION_SEMANTICS_VERSION = 1
_PREPARATION_VERSION = 1
_VISUAL_SEMANTICS_VERSION = 1

_DEFAULT_RC_PARAMS: dict = {
    "figure.figsize": (9.0, 9.0),
    "font.size": 10,
}

#: Colour map for the path-labelled target classes.
_LABEL_COLORS: dict = {
    WALL: "#3a3a3a",
    FREE: "#e8e8e8",
    START: "#2f6f9f",
    GOAL: "#c94f3d",
    PATH: "#f2c220",
}


@dataclass(frozen=True, slots=True)
class MazeHardCaseData:
    """Stable prepared view for ``figure:maze-hard-case/v1``.

    ``domain``/``passable`` come from the authoritative raster-topology source;
    ``start``/``goal``/``reference_labels`` come from the committed task case and
    are carried verbatim. Nothing is recomputed here.
    """

    domain: dict
    passable: tuple[bool, ...]
    start: int
    goal: int
    reference_labels: tuple[str, ...]

    @property
    def width(self) -> int:
        return int(self.domain["width"])

    @property
    def height(self) -> int:
        return int(self.domain["height"])


_INPUT_REQUIREMENT = FigureInputRequirement(
    role="topology",
    contract=RASTER_TOPOLOGY_SCHEMA_REF,
    scope=SCOPE_RECORD,
)


def _prepare_maze_hard_case(source: object, _projection: object = None) -> object:
    """Build the stable prepared view from an authoritative source.

    ``source`` is a ``ResolvedFigureSource``-like object whose content is a
    committed raster-topology record. The task-case annotation is read from the
    source's ``annotation`` payload when provided by the task inspection path;
    it is optional so the figure can degrade to a source-only problem view.
    """
    content = cast(Any, source)
    source_content = (
        content.get("content", content)
        if isinstance(content, dict)
        else getattr(content, "content", content)
    )
    domain = _as_dict(source_content.get("domain", {}))
    passable = tuple(bool(p) for p in source_content["passable"])
    start = _annotation(source, "start", -1)
    goal = _annotation(source, "goal", -1)
    labels = _annotation(source, "reference_labels", None)
    if labels is None:
        # No committed task target supplied: build a base free/wall view from
        # authoritative passability only (no reconstruction of semantics).
        labels = tuple(FREE if p else WALL for p in passable)
        if start >= 0:
            labels = list(labels)
            labels[start] = START
            labels = tuple(labels)
        if goal >= 0:
            labels = list(labels)
            labels[goal] = GOAL
            labels = tuple(labels)
    return MazeHardCaseData(
        domain=domain,
        passable=passable,
        start=start,
        goal=goal,
        reference_labels=tuple(labels),
    )


def _as_dict(value: object) -> dict:
    if isinstance(value, dict):
        return value
    return {}


def _annotation(source: object, key: str, default):
    annotation = getattr(source, "annotation", None)
    if isinstance(annotation, dict) and key in annotation:
        return annotation[key]
    return default


def _hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    """Convert a ``#rrggbb`` hex colour to an ``(r, g, b)`` float tuple [0,1]."""
    hex_color = hex_color.lstrip("#")
    return (  # type: ignore[return-value]
        int(hex_color[0:2], 16) / 255.0,
        int(hex_color[2:4], 16) / 255.0,
        int(hex_color[4:6], 16) / 255.0,
    )


def _realize_maze_hard_case(projection: object) -> object:
    """Render the MazeHard case as a Matplotlib figure (scientific encoding only)."""
    import matplotlib.pyplot as plt

    view = cast(Any, projection).content
    if not isinstance(view, MazeHardCaseData):
        raise TypeError("maze-hard-case figure received an unexpected prepared view")

    labels = view.reference_labels
    width, height = view.width, view.height
    rgb = [_hex_to_rgb(_LABEL_COLORS[label]) for label in labels]
    img = [rgb[i * width : (i + 1) * width] for i in range(height)]

    fig, ax = plt.subplots()
    ax.imshow(img, interpolation="nearest", aspect="equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("MazeHard case: maze, start, goal, and committed reference route")
    return fig


@dataclass(frozen=True, slots=True)
class MazeHardCaseFigure:
    """The ``figure:maze-hard-case/v1`` reusable scientific task figure."""

    ref: ComponentRef = field(default_factory=lambda: ComponentRef.parse(MAZE_HARD_CASE_REF))
    kind: str = field(default=FIGURE_KIND)
    projection: _ProjectionPartition = field(
        default_factory=lambda: _ProjectionPartition(
            semantics_version=_PROJECTION_SEMANTICS_VERSION,
            preparation_version=_PREPARATION_VERSION,
            requirement=_INPUT_REQUIREMENT,
            prepare=_prepare_maze_hard_case,
        )
    )
    visual: _VisualPartition = field(
        default_factory=lambda: _VisualPartition(
            semantics_version=_VISUAL_SEMANTICS_VERSION,
            realize=_realize_maze_hard_case,
        )
    )
    defaults: _DefaultsPartition = field(
        default_factory=lambda: _DefaultsPartition(rc_params=dict(_DEFAULT_RC_PARAMS))
    )


#: The canonical MazeHard task-case figure instance contributed by the provider.
MAZE_HARD_CASE_FIGURE: FigureSpec = MazeHardCaseFigure()
