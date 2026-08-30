"""Framework-owned raster-topology inspection figure (Phase 1 bootstrap slice).

This is the one concrete framework-owned figure introduced by Phase 1
(``figure:raster-topology-inspection/v1``). Its complete scientific/structural
meaning is expressible exclusively through the framework-owned
``raster-topology/v1`` logical contract (Phase-1 § 6 · P1-T4).

The figure understands:

```text
raster-topology/v1
extent (height/width)
passability
```

It must not understand:

```text
DungeonGen, Maze-ND, Arena
rooms, corridors
generator retries
producer configuration
task goals
observations
model predictions
```

A test fixture or future producer yielding an equivalent ``raster-topology/v1``
record requires no semantic modification here (P1-T4 acceptance criterion).

## projection partition (``prepare``)

``prepare`` normalizes the exact stable authoritative source into a stable
typed :class:`~ehp_sn.contracts.topology.RasterTopology` view. A committed
``raster-topology/v1`` record's logical contents are its authoritative
``content()`` projection (a JSON ``{"extent": {...}, "passable": [...]}``
dictionary); ``prepare`` reconstructs the conforming typed view from those
authoritative fields. It derives no new scientific/structural conclusion beyond
what the authoritative contract already states (Phase-1 § 11 · P1-T9);
``rectangular_row_column_domain``/``raster_topology`` are the contract's own
constructors, and every derived view they compute is a canonical fixed
``raster-topology/v1`` derivation.

## visual partition (``realize``)

The figure has one visual objective: communicate which positions are traversable
versus non-traversable in the authoritative raster topology (Phase-1 § 13 ·
P1-T11). Realization uses one Matplotlib Figure, one Axes, and one raster/image
representation. The fact that this figure has one semantic visual unit and one
Axes is **not** generalized into ``Panel == Axes``; no panel/layout abstraction
is introduced (P1-T11).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final, cast

from ehp_sn.contracts.domains import (
    rectangular_row_column_domain,
)
from ehp_sn.contracts.topology import SCHEMA_REF as RASTER_TOPOLOGY_SCHEMA_REF
from ehp_sn.contracts.topology import RasterTopology, raster_topology
from ehp_sn.experiments import ComponentRef
from ehp_sn.figures.contracts import (
    FIGURE_KIND,
    FigureInputRequirement,
    FigureSpec,
    _DefaultsPartition,
    _ProjectionPartition,
    _VisualPartition,
)
from ehp_sn.figures.projection import FigureProjection

#: The canonical component reference of the raster-topology inspection figure.
RASTER_TOPOLOGY_INSPECTION_REF = "figure:raster-topology-inspection/v1"

#: The projection-semantics version of ``figure:raster-topology-inspection/v1``.
_PROJECTION_SEMANTICS_VERSION: Final = 1

#: The preparation-semantics version of the figure (how ``prepare`` interprets
#: the authoritative source into the prepared view).
_PREPARATION_VERSION: Final = 1

#: The visual-semantics version of the figure (its scientific graphical meaning).
_VISUAL_SEMANTICS_VERSION: Final = 1

#: The semantic input requirement: role ``topology`` satisfied by
#: ``raster-topology/v1`` (Phase-1 § 8 · P1-T6).
_INPUT_REQUIREMENT = FigureInputRequirement(
    role="topology",
    contract=RASTER_TOPOLOGY_SCHEMA_REF,
)

#: Private/provisional Phase-1 presentation defaults. These are confined to
#: presentation and never participate in projection identity (P1-T5/P1-T13).
_DEFAULT_RC_PARAMS: Final = {
    "figure.figsize": (6.0, 6.0),
    "font.size": 10,
}

#: Traversable (passable) cell colour.
_PASSABLE_COLOR: Final = "#2f6f4f"
#: Non-traversable (blocked) cell colour.
_BLOCKED_COLOR: Final = "#d8d8d8"


@dataclass(frozen=True, slots=True)
class RasterTopologyInspectionFigure:
    """The phase-1 ``figure:raster-topology-inspection/v1`` executable figure.

    A registered ``DiscoverableDefinition`` (``ref`` + ``kind = "figure"``) with
    projection and visual partitions. It participates in the ordinary component
    catalogue; there is no parallel figure registry.
    """

    ref: ComponentRef = field(default_factory=lambda: ComponentRef.parse(RASTER_TOPOLOGY_INSPECTION_REF))
    kind: str = field(default=FIGURE_KIND)
    projection: _ProjectionPartition = field(
        default_factory=lambda: _ProjectionPartition(
            semantics_version=_PROJECTION_SEMANTICS_VERSION,
            preparation_version=_PREPARATION_VERSION,
            requirement=_INPUT_REQUIREMENT,
            prepare=_prepare_authoritative_topology,
        )
    )
    visual: _VisualPartition = field(
        default_factory=lambda: _VisualPartition(
            semantics_version=_VISUAL_SEMANTICS_VERSION,
            realize=_realize_topology_inspection,
            # The passability colour mapping is scientific visual semantics: the
            # figure encodes traversable vs non-traversable meaning, so a
            # presentation policy must not silently replace it (Phase-4 ·
            # P4-T11). ``image.cmap`` is therefore protected.
            protected_rc_params=frozenset({"image.cmap"}),
        )
    )
    defaults: _DefaultsPartition = field(
        default_factory=lambda: _DefaultsPartition(rc_params=dict(_DEFAULT_RC_PARAMS))
    )


def _extract_authoritative_topology(content: object) -> RasterTopology:
    """Reconstruct the authoritative ``raster-topology/v1`` typed view.

    Accepts either an already-typed :class:`RasterTopology` (producer/in-memory
    context) or the authoritative committed ``content()`` projection dictionary
    (``{"extent": {...}, "passable": [...]}``). It reads only the contract's
    authoritative fields and delegates to the contract's own constructors —
    never a producer or physical-storage detail.
    """
    if isinstance(content, RasterTopology):
        return content
    if not isinstance(content, dict):
        raise TypeError(
            f"raster-topology/v1 figure source must be a typed RasterTopology or its "
            f"authoritative content projection; got {type(content).__name__}"
        )
    extent = content.get("extent")
    passable = content.get("passable")
    if not isinstance(extent, dict) or not isinstance(passable, (list, tuple)):
        raise TypeError(
            "raster-topology/v1 authoritative content projection is missing 'extent' and/or 'passable'"
        )
    try:
        height = int(extent["height"])
        width = int(extent["width"])
    except (KeyError, TypeError, ValueError) as exc:
        raise TypeError("raster-topology/v1 extent projection is missing integer height/width") from exc
    ambient = rectangular_row_column_domain(height, width)
    return raster_topology(ambient, list(passable))


def _prepare_authoritative_topology(source: object) -> object:
    """``prepare``: convert the validated authoritative source to a stable typed view.

    This is intentionally nearly identity-like (Phase-1 § 11 · P1-T9): it
    obtains the authoritative extent and passability, reconstructs the conforming
    :class:`RasterTopology` typed view, and returns it as the stable prepared
    view. It derives no new scientific/structural conclusion beyond the
    authoritative contract.
    """
    return _extract_authoritative_topology(source)


def _realize_topology_inspection(projection: FigureProjection) -> Any:
    """``realize``: draw the projection as a direct Matplotlib Figure.

    Uses one Figure, one Axes, one raster representation (``imshow`` of
    passability), plus minimal structural labels. Uses explicit object-oriented
    Matplotlib operations, not implicit current-figure/current-axes state
    (Phase-1 § 14 · P1-T12).
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap

    topology = cast(RasterTopology, projection.content)
    height = topology.extent.height
    width = topology.extent.width
    passable = topology.passable

    # A 2D display view: row-major passability reshaped to (height, width).
    grid = []
    for row in range(height):
        start = row * width
        grid.append([1 if passable[start + col] else 0 for col in range(width)])

    figure, axes = plt.subplots(1, 1)
    cmap = ListedColormap([_BLOCKED_COLOR, _PASSABLE_COLOR])
    axes.imshow(grid, cmap=cmap, interpolation="nearest", aspect="equal")
    axes.set_title("Raster topology — passable vs non-traversable")
    axes.set_xlabel("column")
    axes.set_ylabel("row")
    axes.set_xticks(range(width))
    axes.set_yticks(range(height))
    return figure


#: The canonical frame-work owned raster-topology inspection figure instance.
RASTER_TOPOLOGY_INSPECTION_FIGURE: FigureSpec = RasterTopologyInspectionFigure()


__all__ = [
    "RASTER_TOPOLOGY_INSPECTION_FIGURE",
    "RASTER_TOPOLOGY_INSPECTION_REF",
]
