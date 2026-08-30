"""Test-only graph companion figure for the ``test-figure-provider`` fixture.

This figure (``figure:digraph-summary/v1``) is a **test-only** FigureSpec
contributed by the independently installed ``test-figure-provider`` fixture
distribution through the ``ehp_sn.figures.providers`` entry-point group. It is
compatible with ``simple-digraph/v1`` (same role ``graph``) but is *not* the
framework-owned record inspector (``figure:simple-digraph-inspection/v1``),
which is a built-in figure in ``ehp_sn``.

Its purpose (Phase-2 § 39-40) is:

- to prove the real installed-provider discovery seam contributes an external,
  non-built-in compatible figure into the ordinary component catalogue;
- to make ``--figure auto`` over a ``simple-digraph/v1`` record **ambiguous**
  (the built-in inspector and this test-only figure both match), so ambiguity
  handling is exercised without adding a second *production* figure.

It is intentionally trivial (a text-only summary) and never models science.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final, cast

from ehp_sn.contracts.relations import SCHEMA_REF as SIMPLE_DIGRAPH_SCHEMA_REF
from ehp_sn.contracts.relations import SimpleDigraph, simple_digraph
from ehp_sn.discovery import ComponentRegistry
from ehp_sn.experiments import ComponentRef
from ehp_sn.figures.contracts import (
    FIGURE_KIND,
    FigureInputRequirement,
    _DefaultsPartition,
    _ProjectionPartition,
    _VisualPartition,
)
from ehp_sn.figures.projection import FigureProjection

#: The canonical reference of the test-only graph companion figure.
DIGRAPH_SUMMARY_REF = "figure:digraph-summary/v1"

#: The companion figure's input requirement (same role/contract as the built-in
#: graph inspector, creating ambiguity for ``--figure auto``).
_COMPANION_REQUIREMENT = FigureInputRequirement(
    role="graph",
    contract=SIMPLE_DIGRAPH_SCHEMA_REF,
)

_COMPANION_RC_PARAMS: Final = {"figure.figsize": (5.0, 3.0), "font.size": 9}


@dataclass(frozen=True, slots=True)
class DigraphSummaryFigure:
    """An intentionally trivial test-only companion ``FigureSpec``.

    Consumes ``simple-digraph/v1`` (same role as the built-in inspector) and
    realizes a minimal text-only summary. It exists so the installed fixture
    provider contributes an external compatible figure that (a) proves the
    real provider seam and (b) makes ``--figure auto`` ambiguous with the
    built-in inspector (Phase-2 § 39-40). It is never a second production
    figure.
    """

    ref: ComponentRef = field(default_factory=lambda: ComponentRef.parse(DIGRAPH_SUMMARY_REF))
    kind: str = field(default=FIGURE_KIND)
    projection: _ProjectionPartition = field(
        default_factory=lambda: _ProjectionPartition(
            semantics_version=1,
            preparation_version=1,
            requirement=_COMPANION_REQUIREMENT,
            prepare=_prepare_summary,
        )
    )
    visual: _VisualPartition = field(
        default_factory=lambda: _VisualPartition(
            semantics_version=1,
            realize=_realize_summary,
        )
    )
    defaults: _DefaultsPartition = field(
        default_factory=lambda: _DefaultsPartition(rc_params=dict(_COMPANION_RC_PARAMS))
    )


def _prepare_summary(source: object) -> object:
    """A minimal identity-like prepare that exposes the authoritative node count."""
    if isinstance(source, SimpleDigraph):
        return {"node_count": source.node_count}
    if isinstance(source, dict):
        node_count = source.get("node_count")
        edges = source.get("edges")
        if not isinstance(node_count, int) or not isinstance(edges, (list, tuple)):
            raise TypeError("digraph-summary/v1 source missing authoritative node_count/edges")
        digraph = simple_digraph(int(node_count), tuple(tuple(e) for e in edges))
        return {"node_count": digraph.node_count}
    raise TypeError(f"digraph-summary/v1 unexpected source type {type(source).__name__}")


def _realize_summary(projection: FigureProjection) -> Any:
    """A trivial text-only realization; no graph layout or RNG."""
    import matplotlib.pyplot as plt

    view = projection.content
    node_count = cast(dict, view)["node_count"]
    figure, axes = plt.subplots(1, 1)
    axes.text(0.5, 0.5, f"simple-digraph summary: {node_count} nodes", ha="center", va="center")
    axes.set_axis_off()
    return figure


def register_digraph_summary(registry: ComponentRegistry) -> None:
    """Register the graph companion figure into ``registry``."""
    registry.register(DigraphSummaryFigure())


__all__ = [
    "DIGRAPH_SUMMARY_REF",
    "DigraphSummaryFigure",
    "register_digraph_summary",
]
