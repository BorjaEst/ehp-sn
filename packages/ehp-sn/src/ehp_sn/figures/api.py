"""Supported public Python figure API (Phase 5D).

This module is the smallest supported Python surface derived from the figure
service that has already survived ``data inspect``, and it is a **façade**:
every function here composes or re-exports the canonical generic figure service
in :mod:`ehp_sn.figures.service` and :mod:`ehp_sn.figures.realization`. It
introduces **no parallel path** (Phase 5D · § 7.3, § 7.9):

```text
no duplicate catalogue
no duplicate selection resolution
no alternative identity derivation
no notebook-specific selection or identity
```

The public capability is deliberately two-stage (prepare, then realize):

```python
projection = prepare_figure(registry, figure_ref, source)
mpl_figure = render_figure_projection(projection)                     # transient
realized   = realize_projection(projection, serialization=policy)     # persistent
```

A single convenience :func:`render_figure` composes the canonical prepare +
realize path; it never implements a parallel path.

Notebook display is just the supported Python API plus an interactive Matplotlib
environment; it introduces no new scientific semantics (``notebook.md`` §
Notebook semantics · Phase 5D § 7.4).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ehp_sn.discovery import ComponentRegistry
from ehp_sn.figures.projection import FigureProjection
from ehp_sn.figures.render_profile import RenderProfile
from ehp_sn.figures.scope import SCOPE_RECORD
from ehp_sn.figures.serialization import ResolvedSerializationPolicy


@dataclass(frozen=True, slots=True)
class FigureSource:
    """The exact resolved source a parent operation hands to the figure path.

    ``src`` is the single exact resolution performed by the parent operation
    (Phase-1 § 10 · P1-T8): the committed artifact's canonical reference, the
    exact record identity, the logical contract the record conforms to, and its
    stable logical contents.

    ``artifact_ref`` is the committed artifact's canonical reference (for
    example ``artifact:arena/default/v1``); ``record_id`` is the exact record
    identity (for example ``sha256:<hex>``); ``schema_ref`` is the framework-
    owned logical contract the record conforms to (for example
    ``raster-topology/v1``); ``content`` is the stable logical contents.
    ``scope`` is the source granularity (``record`` by default); the record
    surface carries only ``record`` scope and is never used for artifact-scope
    collections, which the service resolves directly from a committed artifact.

    This is the public counterpart of the service's exact source surface. It
    carries the same fields and satisfies the same structural source contract,
    so the canonical :func:`prepare_figure` implementation consumes it without
    any source-type branch (Phase 5D § 4.3).
    """

    artifact_ref: str
    record_id: str
    schema_ref: str
    content: object
    scope: str = SCOPE_RECORD


def prepare_figure(
    registry: ComponentRegistry,
    figure_ref: str,
    source: FigureSource,
) -> FigureProjection:
    """Resolve, validate, and project one figure over one exact resolved source.

    This is the canonical public preparation capability (Phase 5D § 7.2). It
    delegates entirely to :func:`ehp_sn.figures.service.prepare_figure`, the
    single implementation also used by ``data inspect`` and every other
    operation; there is no second preparation path.

    ``registry`` is the ordinary figure catalogue to resolve from; ``figure_ref``
    is the canonical figure reference; ``source`` is the single exact resolved
    source (a :class:`FigureSource`) supplied by the parent operation.

    Returns a :class:`~ehp_sn.figures.projection.FigureProjection` carrying
    exact source provenance and (when the figure declares a selection resolver)
    the exact authored + resolved selection.
    """
    from ehp_sn.figures.service import prepare_figure as _prepare_figure

    return _prepare_figure(registry, figure_ref, source)


def render_figure_projection(
    projection: FigureProjection,
    *,
    presentation: RenderProfile | None = None,
    registry: ComponentRegistry | None = None,
) -> Any:
    """Realize a ``FigureProjection`` as a transient Matplotlib Figure (Phase 5D § 7.3).

    Delegates entirely to :func:`ehp_sn.figures.service.render_figure_projection`
    — the same interactive realization path used by inspection. Ownership of the
    returned ``matplotlib.figure.Figure`` transfers to the caller. ``registry``
    is optional (effective catalogue default).

    This is the **interactive** path. For persistent serialized output use
    :func:`realize_projection` instead.
    """
    from ehp_sn.figures.service import render_figure_projection as _render

    return _render(
        projection,
        registry=registry,
        presentation=presentation,
    )


def realize_projection(
    projection: FigureProjection,
    *,
    serialization: ResolvedSerializationPolicy,
    presentation: RenderProfile | None = None,
    registry: ComponentRegistry | None = None,
) -> Any:
    """Serialize one already-fixed projection through the controlled framework path.

    Delegates entirely to :func:`ehp_sn.figures.realization.realize_projection`
    (Phase 4). It resolves one canonical realization request, validates inputs
    before Matplotlib, draws, serializes, and releases the framework-owned
    Figure on every exit path. Returns a :class:`RealizedFigure` with the
    semantic :class:`RealizationIdentity`, a content digest, and separate
    rendering-environment provenance.

    This is the public persistent realization counterpart of the transient
    :func:`render_figure_projection`.
    """
    from ehp_sn.figures.realization import realize_projection as _realize

    return _realize(
        projection,
        serialization=serialization,
        presentation=presentation,
        registry=registry,
    )


def render_figure(
    registry: ComponentRegistry,
    figure_ref: str,
    source: FigureSource,
    *,
    presentation: RenderProfile | None = None,
    serialization: ResolvedSerializationPolicy | None = None,
) -> Any:
    """Compose the canonical prepare + realize path into one call (Phase 5D § 7.3).

    This is a **convenience only**: it composes :func:`prepare_figure` followed
    by :func:`render_figure_projection` (when ``serialization`` is ``None``) or
    :func:`realize_projection` (when persistent output is requested). It
    implements **no parallel path** — both stages are the canonical service
    functions, so the normalized projection semantics and ``ProjectionIdentity``
    are identical to calling the stages directly (or through the CLI).

    Return value:

    - ``serialization is None``: a transient ``matplotlib.figure.Figure``
      (interactive realization; caller owns its lifetime);
    - ``serialization`` given: a ``RealizedFigure`` (persistent serialized
      output with identity and content digest).
    """
    projection = prepare_figure(registry, figure_ref, source)
    if serialization is None:
        return render_figure_projection(projection, registry=registry, presentation=presentation)
    return realize_projection(
        projection,
        serialization=serialization,
        presentation=presentation,
        registry=registry,
    )


__all__ = [
    "FigureSource",
    "prepare_figure",
    "realize_projection",
    "render_figure",
    "render_figure_projection",
]
