"""``test-figure-provider`` test fixture distribution.

This package is an **independently installed test distribution** used by
EHP-SN Phase 2 to prove the real provider-extension seam: an external package
advertising a figure provider under ``ehp_sn.figures.providers`` contributes
test-only companion ``FigureSpec``s (compatible with ``simple-digraph/v1`` and
``categorical-field/v1``) that resolve through the same ordinary component
catalogue and figure-service path as the framework built-in record inspectors.

The framework-built-in record inspectors
(``figure:simple-digraph-inspection/v1``,
``figure:categorical-field-inspection/v1``) live in ``ehp_sn`` and are **not**
re-registered here.

It is not shipped nor imported by production ``ehp_sn``/``ehp_research``.
"""

from __future__ import annotations

from .graph import (
    DIGRAPH_SUMMARY_REF,
    DigraphSummaryFigure,
    register_digraph_summary,
)
from .provider import (
    FIELD_SUMMARY_REF,
    FieldSummaryFigure,
    figure_provider,
)

__all__ = [
    "DIGRAPH_SUMMARY_REF",
    "DigraphSummaryFigure",
    "FIELD_SUMMARY_REF",
    "FieldSummaryFigure",
    "figure_provider",
    "register_digraph_summary",
]
