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
from ehp_sn.figures.projection import FigureProjection, ResolvedFigureSelection

#: The component kind under which a ``FigureSpec`` registers in the ordinary
#: component catalogue.
FIGURE_KIND = "figure"

#: The selection-resolver protocol a ``FigureSpec`` projection partition may
#: expose. A figure without scientific selection leaves ``select`` as ``None``.
#: It receives the validated authoritative source and returns the exact, fully
#: resolved selection (authored semantics + resolved identities) as projection
#: provenance. It must be deterministic (see ``projection.md`` § "Deterministic
#: selection").
FigureSelectionResolver = Callable[[object], ResolvedFigureSelection]


class FigureInputCompatibilityError(ValueError):
    """A figure's declared semantic input requirement cannot be satisfied.

    Raised before preparation/rendering begins, when the resolved source's
    logical contract does not satisfy the figure's declared input requirement.
    It is a controlled figure-input failure, never a missing key,
    ``AttributeError``, shape failure, or raw ``imshow`` failure
    (Phase-1 § 8, P1-T6).
    """


class InspectionCapacityExceeded(ValueError):
    """A record's exact faithful realization exceeds supported inspection capacity.

    Raised when the figure's operational inspection capacity cannot faithfully
    represent the full scientific content of a record (for example a categorical
    vocabulary with more distinct categories than the realization can
    distinguish, or an impractically large extent). Inspection must not silently
    sample, truncate, downsample, or collapse scientific categories to fit
    presentation capacity (Phase-3 § 32, § 36 · SRF-019). The failure is
    deterministic and controlled; it never alters scientific record identity or
    ``ProjectionIdentity``.
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
    semantics version, its preparation semantics version, the ``prepare()``
    implementation that converts a validated authoritative source into a stable
    prepared scientific view, and (when the figure performs scientific
    selection) the ``select()`` resolver that turns the authoritative source
    into an exact ``ResolvedFigureSelection``.

    None of this references visual/Matplotlib/presentation concepts.
    """

    semantics_version: int
    preparation_version: int
    requirement: FigureInputRequirement
    prepare: Callable[[object], object]
    select: FigureSelectionResolver | None = None


@dataclass(frozen=True, slots=True)
class _VisualPartition:
    """The visual (scientific-encoding) partition of a ``FigureSpec``.

    Holds the figure's visual-semantics version and the ``realize()``
    implementation that draws a ``FigureProjection`` as a Matplotlib Figure.

    ``protected_rc_params`` names Matplotlib rc-parameter keys whose value is
    **scientific visual semantics** owned by the figure (for example an
    ``image.cmap`` or colormap-normalization default the visual semantics hard
    codes). A :class:`~ehp_sn.figures.render_profile.RenderProfile` or framework
    override must not silently replace these: doing so would change scientific
    meaning. The framework rejects such a conflict explicitly (Phase-4 ·
    P4-T11), rather than letting presentation reinterpret the science.

    It does not own physical publication dimensions, serialization format, or
    projection selection.
    """

    semantics_version: int
    realize: Callable[[FigureProjection], Any]
    protected_rc_params: frozenset[str] = frozenset()


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
    "FigureSelectionResolver",
    "FigureSpec",
]
