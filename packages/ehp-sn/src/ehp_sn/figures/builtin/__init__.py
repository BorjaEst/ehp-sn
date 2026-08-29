"""Framework-owned built-in figure definitions (Phase 1 bootstrap slice).

Phase 1 contributes exactly one framework-owned built-in figure: the
raster-topology inspection figure. Its complete semantic meaning is defined
only through the framework-owned ``raster-topology/v1`` logical contract, so it
belongs in ``ehp_sn`` (Phase-1 § 6 · P1-T4).

A test fixture or future producer yielding an equivalent ``raster-topology/v1``
record requires no semantic modification to the figure implementation
(Phase-1 § 6 · P1-T4 acceptance criterion).
"""

from __future__ import annotations

from .raster_topology import RASTER_TOPOLOGY_INSPECTION_FIGURE

__all__ = [
    "RASTER_TOPOLOGY_INSPECTION_FIGURE",
    "BUILTIN_FIGURES",
]

#: The ordered tuple of framework-owned built-in figures contributed to the
#: ordinary component catalogue.
BUILTIN_FIGURES = (RASTER_TOPOLOGY_INSPECTION_FIGURE,)
