"""Reusable scientific analysis results owned by ``ehp_research``.

This package holds reusable, task-neutral scientific analysis **results** —
already-computed authoritative quantities presented as stable, immutable values
that downstream consumers (for example research figures) read without
recomputing.

A result here is an authoritative representation of an analysis that was
produced by an upstream scientific analysis authority. It is not an analysis
executor, and it never performs scientific inference, statistical estimation,
or metric computation itself.
"""

from __future__ import annotations

from .hpc import HpcAnalysis, HpcCell, HpcRateMapDomain, hpc_analysis

__all__ = [
    "HpcAnalysis",
    "HpcCell",
    "HpcRateMapDomain",
    "hpc_analysis",
]
