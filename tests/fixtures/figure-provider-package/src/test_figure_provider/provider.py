"""Figure provider for the ``test-figure-provider`` fixture distribution.

This distribution advertises one provider under the framework figure-provider
entry-point group (``ehp_sn.figures.providers``):

```toml
[project.entry-points."ehp_sn.figures.providers"]
test-provider = "test_figure_provider.provider:figure_provider"
```

A provider is a callable ``(ComponentRegistry) -> None`` that registers the
figures it owns. One entry point is one *provider*, not one figure: this
provider contributes two ``FigureSpec``s to prove provider cardinality
(Phase-2 § 7, P2-C) — the semantic graph figure over ``simple-digraph/v1`` and
one intentionally trivial companion figure.

This is explicitly **not** production ``ehp_sn``/``ehp_research`` code. It is a
test fixture distribution used to prove the real installed-provider extension
seam. It stays outside canonical discovery paths of the production framework and
is only visible when installed into the test environment (Phase-2 § 5, § 16.2).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final, cast

from ehp_sn.contracts.relations import SCHEMA_REF as SIMPLE_DIGRAPH_SCHEMA_REF
from ehp_sn.discovery import ComponentRegistry
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

from .graph import SIMPLE_DIGRAPH_INSPECTION_FIGURE, SIMPLE_DIGRAPH_INSPECTION_REF

#: The canonical reference of the trivial companion figure.
_TRIVIAL_DIGRAPH_REF = "figure:digraph-summary/v1"

#: The companion figure's input requirement (same role/contract as the graph figure).
_COMPANION_REQUIREMENT = FigureInputRequirement(
    role="graph",
    contract=SIMPLE_DIGRAPH_SCHEMA_REF,
)

_COMPANION_RC_PARAMS: Final = {"figure.figsize": (5.0, 3.0), "font.size": 9}


@dataclass(frozen=True, slots=True)
class DigraphSummaryFigure:
    """An intentionally trivial companion ``FigureSpec`` (provider cardinality).

    Exists only so the provider advertises more than one definition, proving
    the framework supports ``one provider → zero or more FigureSpecs`` without
    encoding a ``one entry point = one figure`` assumption (Phase-2 § 7). It
    consumes ``simple-digraph/v1`` and realizes a minimal text-only summary.
    """

    ref: ComponentRef = field(default_factory=lambda: ComponentRef.parse(_TRIVIAL_DIGRAPH_REF))
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
    from ehp_sn.contracts.relations import SimpleDigraph, simple_digraph

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


#: The two definitions contributed by this distribution's provider.
_PROVIDER_FIGURES: tuple[FigureSpec, ...] = (
    SIMPLE_DIGRAPH_INSPECTION_FIGURE,
    DigraphSummaryFigure(),
)


def figure_provider(registry: ComponentRegistry) -> None:
    """Register every figure this distribution owns into ``registry``.

    This is the advertised provider entry point. It registers the graph figure
    (``figure:simple-digraph-inspection/v1``) and the trivial companion figure
    (``figure:digraph-summary/v1``) into the ordinary component catalogue.
    Registration uses canonical component references; conflicting duplicate
    canonical references are rejected by the registry (``ARCH-003``).
    """
    for figure in _PROVIDER_FIGURES:
        registry.register(figure)


__all__ = [
    "SIMPLE_DIGRAPH_INSPECTION_REF",
    "figure_provider",
]
