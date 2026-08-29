"""Figure provider for reusable research figures (Phase 3).

This module is the single figure-provider entry point for ``ehp_research``. It
is advertised under the framework's figure-provider entry-point group
``ehp_sn.figures.providers`` (``pyproject.toml``), so reusable research figures
enter the **same ordinary figure catalogue** as the framework's built-in figures
— there is no independent research figure registry (P3-T25).

A provider is a callable ``(ComponentRegistry) -> None``; one entry point is one
provider, and a provider may contribute zero or more ``FigureSpec``s. This
provider currently contributes the HPC place-summary figure.
"""

from __future__ import annotations

from ehp_sn.discovery import ComponentRegistry
from ehp_sn.figures.contracts import FigureSpec

from .hpc_place_summary import HPC_PLACE_SUMMARY_FIGURE

#: The reusable scientific figures this package contributes to the catalogue.
_RESEARCH_FIGURES: tuple[FigureSpec, ...] = (HPC_PLACE_SUMMARY_FIGURE,)


def figure_provider(registry: ComponentRegistry) -> None:
    """Register every reusable research figure into ``registry``.

    Registration uses canonical component references; conflicting duplicate
    canonical references are rejected by the generic registry (``ARCH-003``).
    This is the ordinary figure-provider path — no parallel figure registry.
    """
    for figure in _RESEARCH_FIGURES:
        registry.register(figure)


__all__ = ["figure_provider"]
