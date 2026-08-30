"""Framework-owned built-in figure definitions (Phase 1 + Phase 2 + Phase 4B).

Phase 1 contributes the raster-topology inspection figure
(``figure:raster-topology-inspection/v1``). Phase 2 adds two materially
different contract-level record figures — the simple-digraph inspection figure
(``figure:simple-digraph-inspection/v1`` over ``simple-digraph/v1``) and the
categorical-field inspection figure (``figure:categorical-field-inspection/v1``
over ``categorical-field/v1``).

Phase 4 adds the three artifact-scope summary figures
(``figure:*-artifact-summary/v1``) over collections of contract-conforming
records (Phase-4 § 19-20, § 24-26): generic artifact summaries that consume the
same framework-owned logical contracts but at artifact scope, with deterministic
inspection descriptors and representative galleries. They do not introduce new
artifact families or contract-specific source types.

Each figure's complete semantic meaning is defined only through a framework-owned
logical contract, so each belongs in ``ehp_sn`` (Phase-1 § 6 · P1-T4; Phase-2 § 7,
§ 17; Phase-4 § 19).

A test fixture or future producer yielding an equivalent record — including
structures outside stronger producer invariants (for example a cyclic
``simple-digraph/v1`` graph) — requires no semantic modification to the figure
implementation (Phase-2 § 14; Phase-4 · H4-2).
"""

from __future__ import annotations

from .categorical_field import CATEGORICAL_FIELD_INSPECTION_FIGURE
from .categorical_field_artifact_summary import (
    CATEGORICAL_FIELD_ARTIFACT_SUMMARY_FIGURE,
)
from .raster_topology import RASTER_TOPOLOGY_INSPECTION_FIGURE
from .raster_topology_artifact_summary import RASTER_TOPOLOGY_ARTIFACT_SUMMARY_FIGURE
from .simple_digraph import SIMPLE_DIGRAPH_INSPECTION_FIGURE
from .simple_digraph_artifact_summary import SIMPLE_DIGRAPH_ARTIFACT_SUMMARY_FIGURE

__all__ = [
    "CATEGORICAL_FIELD_ARTIFACT_SUMMARY_FIGURE",
    "CATEGORICAL_FIELD_INSPECTION_FIGURE",
    "RASTER_TOPOLOGY_ARTIFACT_SUMMARY_FIGURE",
    "RASTER_TOPOLOGY_INSPECTION_FIGURE",
    "SIMPLE_DIGRAPH_ARTIFACT_SUMMARY_FIGURE",
    "SIMPLE_DIGRAPH_INSPECTION_FIGURE",
    "BUILTIN_FIGURES",
]

#: The ordered tuple of framework-owned built-in figures contributed to the
#: ordinary component catalogue.
BUILTIN_FIGURES = (
    RASTER_TOPOLOGY_INSPECTION_FIGURE,
    SIMPLE_DIGRAPH_INSPECTION_FIGURE,
    CATEGORICAL_FIELD_INSPECTION_FIGURE,
    RASTER_TOPOLOGY_ARTIFACT_SUMMARY_FIGURE,
    SIMPLE_DIGRAPH_ARTIFACT_SUMMARY_FIGURE,
    CATEGORICAL_FIELD_ARTIFACT_SUMMARY_FIGURE,
)
