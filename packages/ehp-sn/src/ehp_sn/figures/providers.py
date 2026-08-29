"""Framework figure provider contribution (Phase 1 + Phase 2).

This module contributes framework-owned built-in figures to the ordinary
component catalogue (Phase 1) and composes installed figure providers that
contribute their own reusable figures (Phase 2).

A figure provider is a callable ``(ComponentRegistry) -> None`` that registers
the figures it owns. Built-in figures are contributed directly through
:func:`register_builtin_figures`; externally installed distributions advertise a
provider under the entry-point group ``ehp_sn.figures.providers``, discovered
through the same generic installed-provider composition root the framework uses
for every component kind (``ehp_sn.discovery.register_installed_providers``).

There is deliberately **no parallel figure registry**. A ``FigureSpec`` is
registered into the same generic :class:`~ehp_sn.discovery.ComponentRegistry`
that every component uses, keyed by kind ``figure``
(``core.md`` § "Catalogue semantics"). Once contributed, resolving a figure does
not require knowing whether it originated from ``ehp_sn``, ``ehp_research``, a
test package, or a future external package. Removing a figure's definition from
its provider makes ordinary catalogue resolution fail; no second registry
re-resolves it.
"""

from __future__ import annotations

from ehp_sn.discovery import ComponentRegistry, register_installed_providers

#: Entry-point group under which installed packages advertise figure providers.
#: An external provider is a callable ``(ComponentRegistry) -> None`` that
#: registers the figures it owns. One entry point is one *provider*, not one
#: figure: a provider may contribute zero or more ``FigureSpec``s.
FIGURE_PROVIDER_ENTRY_POINT_GROUP = "ehp_sn.figures.providers"


def register_builtin_figures(registry: ComponentRegistry) -> ComponentRegistry:
    """Register every framework-owned built-in figure into ``registry``.

    The framework owns exactly one built-in figure: the raster-topology
    inspection figure (``figure:raster-topology-inspection/v1``). Its complete
    semantic meaning is expressible exclusively through the framework-owned
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


def register_installed_figure_providers(registry: ComponentRegistry) -> ComponentRegistry:
    """Invoke every installed figure provider under :data:`FIGURE_PROVIDER_ENTRY_POINT_GROUP`.

    This reuses the generic installed-provider composition root
    (:func:`ehp_sn.discovery.register_installed_providers`) with the figure
    provider entry-point group. It does **not** introduce a figure-specific
    plugin system, retry, quarantine, or recovery (Phase-2 § 17); provider
    failures surface through the existing generic provider/catalogue policy.

    Returns ``registry`` for chaining. When no provider is installed, the
    registry is returned unchanged; propagation via ``pip install -e`` or a
    corresponding package-manager step is what makes a provider visible.
    """
    return register_installed_providers(registry, group=FIGURE_PROVIDER_ENTRY_POINT_GROUP)


def effective_figure_registry() -> ComponentRegistry:
    """Build the ordinary component catalogue: built-in + installed figures.

    This is the composition root for the figure path: a fresh, ordinary
    :class:`~ehp_sn.discovery.ComponentRegistry` containing the framework's
    built-in figures **and** every installed figure provider's contributed
    figures. Built-in and externally contributed figures enter the same
    ordinary catalogue and resolve through the same canonical API (Phase-2 ·
    P2-C).

    It deliberately does not alter the generic
    ``ehp_sn.discovery.effective_registry`` (which remains the research
    component-provider catalogue, ``ehp_sn.providers``); figure resolution uses
    the same ``ComponentRegistry`` class and canonical-resolution semantics —
    it is not a separate authoritative registry.
    """
    registry = register_builtin_figures(ComponentRegistry())
    return register_installed_figure_providers(registry)


__all__ = [
    "FIGURE_PROVIDER_ENTRY_POINT_GROUP",
    "effective_figure_registry",
    "register_builtin_figures",
    "register_installed_figure_providers",
]
