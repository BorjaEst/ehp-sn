"""``test-figure-provider`` test fixture distribution.

This package is an **independently installed test distribution** used by
EHP-SN Phase 2 to prove the real provider-extension seam: an external package
advertising a figure provider under ``ehp_sn.figures.providers`` contributes a
non-raster FigureSpec (``figure:simple-digraph-inspection/v1``) that resolves
through the same ordinary component catalogue and figure-service path as the
built-in raster figure.

It is not shipped nor imported by production ``ehp_sn``/``ehp_research``.
"""

from __future__ import annotations

from .graph import (
    SIMPLE_DIGRAPH_INSPECTION_FIGURE,
    SIMPLE_DIGRAPH_INSPECTION_REF,
    SimpleDigraphInspectionData,
)
from .provider import figure_provider

__all__ = [
    "SIMPLE_DIGRAPH_INSPECTION_FIGURE",
    "SIMPLE_DIGRAPH_INSPECTION_REF",
    "SimpleDigraphInspectionData",
    "figure_provider",
]
