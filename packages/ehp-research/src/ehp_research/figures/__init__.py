"""HPC place-summary figure package (Phase 3).

This package holds reusable scientific figure capabilities owned by
``ehp_research`` whose meaning is independent of one concrete experiment. It
implements the generic figure contracts in ``ehp_sn.figures``: scientific source
requirements, deterministic scientific selection, research-owned preparation,
and scientific visual composition.

Framework mechanics (source resolution, figure catalogue participation, the
``FigureProjection`` envelope, generic render execution, serialization) are
owned and referenced from the framework, never redefined here.
"""

from __future__ import annotations

from .hpc_place_summary import HPC_PLACE_SUMMARY_REF, HpcPlaceSummaryData
from .selection import TopSpatialInformationCells

__all__ = [
    "HPC_PLACE_SUMMARY_REF",
    "HpcPlaceSummaryData",
    "TopSpatialInformationCells",
]
