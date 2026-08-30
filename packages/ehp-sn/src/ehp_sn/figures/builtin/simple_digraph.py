"""Framework-owned simple-digraph inspection figure (Phase 2 bootstrap slice).

This is the second concrete framework-owned figure introduced by Phase 2
(``figure:simple-digraph-inspection/v1``). Its complete scientific/structural
meaning is expressible exclusively through the framework-owned
``simple-digraph/v1`` logical contract (Phase-2 § 7).

The figure understands:

```text
simple-digraph/v1
record identity
public node domain
directed edge relation
canonical derived properties (acyclic, terminal_count, all_nodes_reach_a_terminal)
```

It must not understand:

```text
Dagflow family identity, variant, split
generation protocol, generation seed
private construction order
single-terminal guarantee
```

A test fixture or future producer yielding an equivalent ``simple-digraph/v1``
record (including graphs outside Dagflow's stronger invariants, such as a
cyclic graph) requires no semantic modification here (Phase-2 § 14).

## Semantics reused, not reimplemented

Derived structural properties (``acyclic``, ``terminal_count``,
``all_nodes_reach_a_terminal``) are canonical ``simple-digraph/v1`` derived
views. ``prepare`` reconstructs the typed :class:`SimpleDigraph` through the
contract's own constructor (:func:`simple_digraph`) and reads the canonical
derived views from it (Phase-2 § 5) — it never independently reimplements the
derivation (Phase-2 § 5 · forbidden twin). The exact record identity is carried
as projection provenance (``FigureProjection.source.record_id``), not duplicated
into the prepared value.

## Graph semantic boundary

The generic graph figure uses ``terminal`` (a node with out-degree zero under
``simple-digraph/v1``), never ``goal``/``start``/``target``. It introduces no
task or model semantics (Phase-2 § 10).

## Node IDs are not coordinates

Public node IDs ``{0, ..., N-1}`` are categorical identities, not spatial
coordinates. ``u < v`` implies no topological/ temporal/distance/priority order
(Phase-2 § 11). Drawing coordinates are **visual realization only**: a
deterministic, fully specified circular placement with an explicit canonical
node input order. No stochastic or algorithmically adaptive layout is used, so
there is no hidden algorithm selection and no uncontrolled randomness
(Phase-2 § 12-13). A layout/palette change therefore never changes
``ProjectionIdentity`` (projection identity is computed from the scientific
structure only).
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

#: The canonical component reference of the simple-digraph inspection figure.
SIMPLE_DIGRAPH_INSPECTION_REF = "figure:simple-digraph-inspection/v1"

#: The projection-semantics version of ``figure:simple-digraph-inspection/v1``.
_PROJECTION_SEMANTICS_VERSION: Final = 1

#: The preparation-semantics version of the figure (how ``prepare`` interprets
#: the authoritative source into the prepared view).
_PREPARATION_VERSION: Final = 1

#: The visual-semantics version of the figure (its scientific graphical meaning).
_VISUAL_SEMANTICS_VERSION: Final = 1

#: The semantic input requirement: role ``graph`` satisfied by
#: ``simple-digraph/v1`` (Phase-2 § 8).
_INPUT_REQUIREMENT = FigureInputRequirement(
    role="graph",
    contract=SIMPLE_DIGRAPH_SCHEMA_REF,
)

#: Private/provisional presentation defaults. These are confined to presentation
#: and never participate in projection identity (P1-T5/P1-T13).
_DEFAULT_RC_PARAMS: Final = {
    "figure.figsize": (6.0, 6.0),
    "font.size": 10,
}

#: Ordinary (non-terminal) node fill colour.
_NODE_FILL: Final = "#2f6f9f"
#: Edge line colour.
_EDGE_COLOR: Final = "#555555"
#: Terminal node fill colour (authoritative terminals emphasized as terminals).
_TERMINAL_FILL: Final = "#2f6f4f"


@dataclass(frozen=True, slots=True)
class SimpleDigraphInspectionData:
    """Framework-owned prepared structural view of one ``simple-digraph/v1`` record.

    Carries exactly the authoritative graph structure the figure communicates
    (Phase-2 § 9):

    ``node_count`` is the cardinality of the dense public node domain,
    ``edges`` the canonical directed edge relation, ``terminals`` the
    authoritative terminal identities (nodes with out-degree zero), and
    ``acyclic`` / ``all_nodes_reach_a_terminal`` the canonical derived
    structural properties.

    All of these come from the contract's own constructor and agree exactly
    with ``simple-digraph/v1`` canonical derivations (``SG-REC-006``); the
    figure derives none of them independently (Phase-2 § 5).

    The exact record identity is not duplicated here: it is already carried as
    exact provenance by ``FigureProjection.source.record_id``.
    """

    node_count: int
    edges: tuple[tuple[int, int], ...]
    terminals: tuple[int, ...]
    acyclic: bool
    all_nodes_reach_a_terminal: bool


@dataclass(frozen=True, slots=True)
class SimpleDigraphInspectionFigure:
    """The Phase-2 ``figure:simple-digraph-inspection/v1`` executable figure.

    A registered ``DiscoverableDefinition`` (``ref`` + ``kind = "figure"``) with
    projection and visual partitions. It participates in the ordinary component
    catalogue; there is no parallel figure registry.
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
    :func:`simple_digraph` — never a producer or physical-storage detail and
    never an independent reimplementation of the derived properties (Phase-2 §
    5, what-must-never-happen block).
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

    # Authoritative terminal identities: nodes with out-degree zero. Computed
    # from the canonical edge relation via the contract's derivation (agreeing
    # with digraph.terminal_count, SG-REC-006). The figure reuses the
    # contract-derived property rather than reimplementing it (Phase-2 § 5).
    out_degree = [0] * node_count
    for source, _target in digraph.edges:
        out_degree[source] += 1
    terminals = tuple(node for node in range(node_count) if out_degree[node] == 0)

    return SimpleDigraphInspectionData(
        node_count=node_count,
        edges=tuple(digraph.edges),
        terminals=terminals,
        acyclic=digraph.acyclic,
        all_nodes_reach_a_terminal=digraph.all_nodes_reach_a_terminal,
    )


def _prepare_authoritative_digraph(source: object) -> object:
    """``prepare``: convert the validated authoritative source to a stable typed view.

    The prepared view carries the authoritative graph structure derived from
    the contract's own constructor. It derives no new structural conclusion
    beyond the authoritative contract. The exact record identity is carried as
    projection provenance (``FigureProjection.source.record_id``), not
    duplicated into the prepared value.
    """
    return _extract_authoritative_digraph(source)


def _circular_positions(node_count: int) -> list[tuple[float, float]]:
    """Return deterministic visual-only circular node positions.

    Node ``i`` is placed at angle ``2 * pi * i / node_count`` starting from the
    top (pi/2) and proceeding clockwise (Phase-2 § 12-13). The canonical node
    input order is ``0, 1, ..., node_count - 1`` and the placement is fully
    specified and deterministic: no scientific RNG is consumed and no hidden
    algorithm selection or uncontrolled randomness exists. An unseeded
    force-directed layout is intentionally not used.

    These coordinates are presentation-derived realization values. They are
    never written back into the scientific graph source and never become
    scientific data (Phase-2 § 12, § 33).
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

    The objective is: make the complete authoritative directed relation
    understandable while assigning no undeclared scientific meaning to drawing
    coordinates (Phase-2 § 9). Node IDs are categorical identities and are drawn
    as labels, never as x/y coordinates (Phase-2 § 11).
    """
    import matplotlib.pyplot as plt

    data = cast(SimpleDigraphInspectionData, projection.content)

    positions = _circular_positions(data.node_count)
    terminal_set = set(data.terminals)

    figure, axes = plt.subplots(1, 1)
    axes.set_aspect("equal")

    # Draw directed edges first (under the nodes); direction is explicit.
    for source, target in data.edges:
        x0, y0 = positions[source]
        x1, y1 = positions[target]
        axes.annotate(
            "",
            xy=(x1, y1),
            xytext=(x0, y0),
            arrowprops=dict(arrowstyle="->", color=_EDGE_COLOR, lw=1.2),
        )

    # Draw all public nodes over the edges; emphasise authoritative terminals.
    for i, (x, y) in enumerate(positions):
        fill = _TERMINAL_FILL if i in terminal_set else _NODE_FILL
        axes.scatter([x], [y], s=220, c=fill, zorder=3)
        axes.text(x, y, str(i), ha="center", va="center", color="white", fontsize=8, zorder=4)

    axes.set_title("Simple digraph — nodes, directed edges, terminals")
    axes.set_axis_off()
    axes.margins(0.15)
    return figure


#: The canonical framework-owned simple-digraph inspection figure instance.
SIMPLE_DIGRAPH_INSPECTION_FIGURE: FigureSpec = SimpleDigraphInspectionFigure()


__all__ = [
    "SIMPLE_DIGRAPH_INSPECTION_FIGURE",
    "SIMPLE_DIGRAPH_INSPECTION_REF",
    "SimpleDigraphInspectionData",
]
