"""Generic framework figure contracts (Phase 1 bootstrap slice).

This module defines the minimal executable figure contracts required to prove
the Phase-1 walking skeleton: a registered ``FigureSpec`` that participates in
the ordinary component catalogue, declares its semantic input requirement, and
separates projection (scientific-view) semantics from visual realization
semantics.

It deliberately introduces **no** selection framework, panel/layout framework,
graphics IR, render-engine hierarchy, serialization, or figure artifact
hierarchy. Those belong to later phases and are explicit non-targets
(Phase-1 § 21).

The normative semantics are owned by ``docs/docs/framework/figures/``
(``core.md``, ``projection.md``, ``rendering.md``); this module implements them
for the bootstrap slice.

## The three partitions

A ``FigureSpec`` has three semantically distinct partitions, matching the
framework specification (``core.md``):

```text
projection
    scientific-view semantics: input requirement, preparation semantics/version,
    prepare() implementation

visual
    scientific visual-encoding semantics: visual semantics/version,
    Matplotlib realization implementation

defaults
    optional realization defaults, confined to presentation and never part of
    projection identity
```

Projection identity must be computable without reading the visual or defaults
partition (``projection.md`` § "Projection identity").
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol

from ehp_sn.experiments import ComponentRef
from ehp_sn.figures.projection import FigureProjection

#: The component kind under which a ``FigureSpec`` registers in the ordinary
#: component catalogue.
FIGURE_KIND = "figure"


class FigureInputCompatibilityError(ValueError):
    """A figure's declared semantic input requirement cannot be satisfied.

    Raised before preparation/rendering begins, when the resolved source's
    logical contract does not satisfy the figure's declared input requirement.
    It is a controlled figure-input failure, never a missing key,
    ``AttributeError``, shape failure, or raw ``imshow`` failure
    (Phase-1 § 8, P1-T6).
    """


@dataclass(frozen=True, slots=True)
class FigureInputRequirement:
    """A figure's declared semantic source requirement for one role.

    ``role`` names what the source means to this figure (for example ``topology``)
    and ``contract`` is the framework-owned logical contract that must satisfy
    that role (for example ``raster-topology/v1``).

    The requirement must not specify physical storage paths, producer identity,
    storage format, or filenames (Phase-1 § 8 · P1-T6; ``projection.md``
    § ``FigureInputContract``).
    """

    role: str
    contract: str

    def accepts(self, logical_contract: str) -> bool:
        """Whether an exact source's logical contract satisfies this requirement."""
        return logical_contract == self.contract


@dataclass(frozen=True, slots=True)
class _ProjectionPartition:
    """The projection (scientific-view) partition of a ``FigureSpec``.

    Holds the figure's declared semantic input requirement, its projection
    semantics version, its preparation semantics version, and the ``prepare()``
    implementation that converts a validated authoritative source into a stable
    prepared scientific view.

    None of this references visual/Matplotlib/presentation concepts.
    """

    semantics_version: int
    preparation_version: int
    requirement: FigureInputRequirement
    prepare: Callable[[object], object]


@dataclass(frozen=True, slots=True)
class _VisualPartition:
    """The visual (scientific-encoding) partition of a ``FigureSpec``.

    Holds the figure's visual-semantics version and the ``realize()``
    implementation that draws a ``FigureProjection`` as a Matplotlib Figure.

    It does not own physical publication dimensions, serialization format, or
    projection selection.
    """

    semantics_version: int
    realize: Callable[[FigureProjection], Any]


@dataclass(frozen=True, slots=True)
class _DefaultsPartition:
    """Optional realization defaults, confined to presentation.

    These values do not participate in projection identity (Phase-1 § 7 ·
    P1-T5; ``core.md`` § "Defaults partition"). They are private/provisional:
    no public ``RenderProfile`` is stabilized in Phase 1.
    """

    rc_params: dict[str, object] = field(default_factory=dict)


class FigureSpec(Protocol):
    """A registered executable figure capability (structural protocol).

    A ``FigureSpec`` is a ``DiscoverableDefinition`` (``ref`` + ``kind``) with
    three observable partitions. The Python representation is provisional; the
    partition separation is the semantic contract (``core.md`` § ``FigureSpec``).

    Only the ordinary component catalogue resolves a ``FigureSpec``; there is no
    parallel figure registry.
    """

    @property
    def ref(self) -> ComponentRef: ...

    @property
    def kind(self) -> str:
        """Must equal ``FIGURE_KIND`` (matching ``ref.kind``)."""
        ...

    @property
    def projection(self) -> _ProjectionPartition: ...

    @property
    def visual(self) -> _VisualPartition: ...

    @property
    def defaults(self) -> _DefaultsPartition: ...


__all__ = [
    "FIGURE_KIND",
    "FigureInputCompatibilityError",
    "FigureInputRequirement",
    "FigureSpec",
]
