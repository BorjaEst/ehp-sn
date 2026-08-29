"""Framework figure provider contribution (Phase 1 bootstrap slice).

This module contributes framework-owned built-in figures to the ordinary
component catalogue. Phase 1 uses framework-owned/built-in providers only;
entry-point discovery from external installed distributions is deferred to
Phase 2 (``core.md`` § "Provider contribution").

The figure entry-point group ``ehp_sn.figures.providers`` is declared here for
the deferred external-provider mechanism, but the framework contributes its own
built-in figures directly through :func:`register_builtin_figures`.

There is deliberately **no parallel figure registry**. A ``FigureSpec`` is
registered into the same generic :class:`~ehp_sn.discovery.ComponentRegistry`
that every component uses, keyed by kind ``figure``
(``core.md`` § "Catalogue semantics"). Removing a built-in figure's definition
from its provider makes ordinary catalogue resolution fail; no second registry
re-resolves it.
"""

from __future__ import annotations

from ehp_sn.discovery import ComponentRegistry

#: Entry-point group under which installed packages would advertise figure
#: providers in Phase 2 (an external provider is a callable
#: ``(ComponentRegistry) -> None`` that registers the figures it owns).
FIGURE_PROVIDER_ENTRY_POINT_GROUP = "ehp_sn.figures.providers"


def register_builtin_figures(registry: ComponentRegistry) -> ComponentRegistry:
    """Register every framework-owned built-in figure into ``registry``.

    Phase 1 owns exactly one built-in figure: the raster-topology inspection
    figure (``figure:raster-topology-inspection/v1``). Its complete semantic
    meaning is expressible exclusively through the framework-owned
    ``raster-topology/v1`` logical contract, which is the justification for its
    placement in ``ehp_sn`` (Phase-1 § 6 · P1-T4).

    Returns ``registry`` for chaining. Registration uses canonical component
    references; conflicting duplicates are rejected by the registry
    (``ARCH-003``).
    """
    from ehp_sn.figures.builtin import BUILTIN_FIGURES

    for figure in BUILTIN_FIGURES:
        registry.register(figure)
    return registry


def effective_figure_registry() -> ComponentRegistry:
    """Build the ordinary component catalogue including framework built-in figures.

    This is the composition root for the figure path: a fresh, ordinary
    :class:`~ehp_sn.discovery.ComponentRegistry` containing the framework's
    built-in figures. It deliberately does not alter the generic
    ``ehp_sn.discovery.effective_registry`` (which remains purely
    installed-provider driven); figure resolution uses the same
    ``ComponentRegistry`` class and canonical-resolution semantics —
    it is not a separate authoritative registry.
    """
    return register_builtin_figures(ComponentRegistry())


__all__ = [
    "FIGURE_PROVIDER_ENTRY_POINT_GROUP",
    "effective_figure_registry",
    "register_builtin_figures",
]
