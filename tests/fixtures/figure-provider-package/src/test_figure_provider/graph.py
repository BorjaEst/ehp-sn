"""Executable graph figure over ``simple-digraph/v1`` (Phase 2).

This figure is contributed by an **independently installed test distribution**
(``test-figure-provider``) through the figure-provider entry-point group
``ehp_sn.figures.providers``. It proves that the exact Phase-1 figure spine
accepts a semantically different, externally contributed figure without the
framework learning anything about graphs, the external package, or provider
order (Phase-2 § 29).

The figure understands:

```text
simple-digraph/v1
node_count
directed edges
terminal identities (nodes with out-degree zero)
```

It must not understand:

```text
raster dimensions / rows / columns / passability / imshow
DungeonGen, Maze-ND, Dagflow, Arena, HRM
producer configuration
model predictions
```

## projection partition (``prepare``)

``prepare`` normalizes the exact stable authoritative source into a stable
typed :class:`~test_figure_provider.graph.SimpleDigraphInspectionData` view.
A committed ``simple-digraph/v1`` record's logical contents are its authoritative
``content()`` projection (a JSON ``{"node_count": N, "edges": [...]}``
dictionary); ``prepare`` reconstructs the conforming typed view from those
authoritative fields via the contract's own constructor
:func:`ehp_sn.contracts.relations.simple_digraph`.

The prepared data carries exactly the contract's authoritative structure:

```text
record identity     — the exact committed record id (provenance)
node identities     — the dense public node domain {0, ..., node_count - 1}
directed edges      — the canonical directed edge relation
terminal identities — nodes with out-degree zero (a canonical contract derivation)
```

Terminal identities are not a new scientific conclusion: they agree exactly with
the contract's derived ``terminal_count`` property (``SG-REC-006``).

## visual partition (``realize``)

The figure has one visual objective: communicate the authoritative graph
structure — node identities, directed edges, and terminal identities.
Realization uses one Matplotlib Figure and one Axes with a deterministic
visual-only node placement.

### Deterministic placement

Graph topology is **not** graph screen coordinates. ``simple-digraph/v1``
contains no authoritative visual coordinates, so node positions are
presentation-derived values. Phase 2 must not introduce a separate
stochastic-layout problem. This figure therefore uses a fixed, fully specified
circular placement:

```text
canonical node ordering (0, 1, ..., node_count - 1)
        ↓
evenly spaced angles around a unit circle
```

The placement does not become scientific source data, does not become a new
scientific result, and does not consume scientific RNG (Phase-2 § 3, P2-10).
An unseeded force-directed layout is deliberately **not** used.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Final, cast

from ehp_sn.contracts.relations import SCHEMA_REF as SIMPLE_DIGRAPH_SCHEMA_REF
from ehp_sn.contracts.relations import (
    SimpleDigraph,
    simple_digraph,
)
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

#: The canonical component reference of the externally contributed graph figure.
SIMPLE_DIGRAPH_INSPECTION_REF = "figure:simple-digraph-inspection/v1"

#: The projection-semantics version of ``figure:simple-digraph-inspection/v1``.
_PROJECTION_SEMANTICS_VERSION: Final = 1

#: The preparation-semantics version of the figure.
_PREPARATION_VERSION: Final = 1

#: The visual-semantics version of the figure.
_VISUAL_SEMANTICS_VERSION: Final = 1

#: The semantic input requirement: role ``graph`` satisfied by
#: ``simple-digraph/v1``.
_INPUT_REQUIREMENT = FigureInputRequirement(
    role="graph",
    contract=SIMPLE_DIGRAPH_SCHEMA_REF,
)

#: Private/provisional presentation defaults (never part of projection identity).
_DEFAULT_RC_PARAMS: Final = {
    "figure.figsize": (6.0, 6.0),
    "font.size": 10,
}

#: Node fill colour for ordinary (non-terminal) nodes.
_NODE_FILL: Final = "#2f6f9f"
#: Edge line colour.
_EDGE_COLOR: Final = "#555555"
#: Terminal node fill colour (authoritative terminals emphasized).
_TERMINAL_FILL: Final = "#2f6f4f"


@dataclass(frozen=True, slots=True)
class SimpleDigraphInspectionData:
    """Provider-owned prepared structural view of one ``simple-digraph/v1`` record.

    Carries exactly the authoritative graph structure the figure communicates:

    ``node_count`` is the cardinality of the dense node domain, ``edges`` the
    canonical directed edge relation, and ``terminals`` the authoritative
    terminal identities (nodes with out-degree zero, agreeing with the
    contract's derived ``terminal_count``).

    The record identity is not duplicated here: it is already carried as exact
    provenance by ``FigureProjection.source.record_id`` (the framework's
    provenance home, shared with the raster figure). Only fields the actual
    contract and visualization require are included.
    """

    node_count: int
    edges: tuple[tuple[int, int], ...]
    terminals: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class SimpleDigraphInspectionFigure:
    """The external ``figure:simple-digraph-inspection/v1`` executable figure.

    A registered ``DiscoverableDefinition`` (``ref`` + ``kind = "figure"``) with
    projection and visual partitions. It participates in the same ordinary
    component catalogue as the built-in raster figure; there is no parallel
    figure registry.
    """

    ref: ComponentRef = field(default_factory=lambda: ComponentRef.parse(SIMPLE_DIGRAPH_INSPECTION_REF))
    kind: str = field(default=FIGURE_KIND)
    projection: _ProjectionPartition = field(
        default_factory=lambda: _ProjectionPartition(
            semantics_version=_PROJECTION_SEMANTICS_VERSION,
            preparation_version=_PREPARATION_VERSION,
            requirement=_INPUT_REQUIREMENT,
            prepare=_prepare_authoritative_digraph,
        )
    )
    visual: _VisualPartition = field(
        default_factory=lambda: _VisualPartition(
            semantics_version=_VISUAL_SEMANTICS_VERSION,
            realize=_realize_digraph_inspection,
        )
    )
    defaults: _DefaultsPartition = field(
        default_factory=lambda: _DefaultsPartition(rc_params=dict(_DEFAULT_RC_PARAMS))
    )


def _extract_authoritative_digraph(content: object) -> SimpleDigraphInspectionData:
    """Reconstruct the authoritative ``simple-digraph/v1`` prepared view.

    Accepts either an already-typed :class:`SimpleDigraph` (producer/in-memory
    context) or the authoritative committed ``content()`` projection dictionary
    (``"node_count"`` + ``"edges"``). It reads only the contract's authoritative
    fields and delegates to the contract's own constructor
    :func:`simple_digraph` — never a producer or physical-storage detail.
    """
    if isinstance(content, SimpleDigraph):
        node_count: int = content.node_count
        edges: tuple[tuple[int, int], ...] = tuple(content.edges)
    elif isinstance(content, dict):
        raw_count = content.get("node_count")
        raw_edges = content.get("edges")
        if not isinstance(raw_count, int) or not isinstance(raw_edges, (list, tuple)):
            raise TypeError(
                "simple-digraph/v1 authoritative content projection is missing "
                "integer 'node_count' and/or 'edges'"
            )
        node_count = int(raw_count)
        edges = tuple(
            (int(source), int(target))
            for source, target in raw_edges  # type: ignore[misc]
        )
    else:
        raise TypeError(
            f"simple-digraph/v1 figure source must be a typed SimpleDigraph or its "
            f"authoritative content projection; got {type(content).__name__}"
        )

    digraph = simple_digraph(node_count, edges)

    # Authoritative terminal identities: nodes with out-degree zero. This is a
    # canonical contract derivation agreeing with digraph.terminal_count
    # (SG-REC-006) — not a new scientific conclusion.
    out_degree = [0] * node_count
    for source, _target in digraph.edges:
        out_degree[source] += 1
    terminals = tuple(node for node in range(node_count) if out_degree[node] == 0)

    return SimpleDigraphInspectionData(
        node_count=node_count,
        edges=tuple(digraph.edges),
        terminals=terminals,
    )


def _prepare_authoritative_digraph(source: object) -> object:
    """``prepare``: convert the validated authoritative source to a stable typed view.

    The prepared view carries the authoritative node/edge/terminal structure
    derived from the contract's own constructor. It derives no new structural
    conclusion beyond the authoritative contract. The exact record identity is
    carried as projection provenance (``FigureProjection.source.record_id``),
    not duplicated into the prepared value.
    """
    return _extract_authoritative_digraph(source)


def _circular_positions(node_count: int) -> list[tuple[float, float]]:
    """Return deterministic visual-only circular node positions.

    Node ``i`` is placed at angle ``2 * pi * i / node_count`` starting from the
    top (pi/2) and proceeding clockwise. No scientific RNG is consumed; the
    placement is purely a presentation-derived realization (Phase-2 § 3,
    P2-10). An unseeded force-directed layout is intentionally not used.
    """
    positions: list[tuple[float, float]] = []
    for i in range(node_count):
        angle = math.pi / 2 - 2.0 * math.pi * i / node_count
        positions.append((math.cos(angle), math.sin(angle)))
    return positions


def _realize_digraph_inspection(projection: FigureProjection) -> Any:
    """``realize``: draw the projection as a direct Matplotlib Figure.

    Uses one Figure and one Axes with deterministic circular node placement,
    directed edges as arrows, and terminals emphasized by a distinct node
    colour. Uses explicit object-oriented Matplotlib operations, not implicit
    current-figure/current-axes state.
    """
    import matplotlib.pyplot as plt

    data = cast(SimpleDigraphInspectionData, projection.content)

    positions = _circular_positions(data.node_count)
    terminal_set = set(data.terminals)

    figure, axes = plt.subplots(1, 1)
    axes.set_aspect("equal")

    # Draw directed edges first (under the nodes).
    for source, target in data.edges:
        x0, y0 = positions[source]
        x1, y1 = positions[target]
        axes.annotate(
            "",
            xy=(x1, y1),
            xytext=(x0, y0),
            arrowprops=dict(arrowstyle="->", color=_EDGE_COLOR, lw=1.2),
        )

    # Draw nodes over the edges; emphasise authoritative terminals.
    for i, (x, y) in enumerate(positions):
        fill = _TERMINAL_FILL if i in terminal_set else _NODE_FILL
        axes.scatter([x], [y], s=220, c=fill, zorder=3)
        axes.text(x, y, str(i), ha="center", va="center", color="white", fontsize=8, zorder=4)

    axes.set_title("Simple digraph — nodes, directed edges, terminals")
    axes.set_axis_off()
    axes.margins(0.15)
    return figure


#: The external graph figure instance contributed by this distribution's provider.
SIMPLE_DIGRAPH_INSPECTION_FIGURE: FigureSpec = SimpleDigraphInspectionFigure()


__all__ = [
    "SIMPLE_DIGRAPH_INSPECTION_FIGURE",
    "SIMPLE_DIGRAPH_INSPECTION_REF",
    "SimpleDigraphInspectionData",
]
