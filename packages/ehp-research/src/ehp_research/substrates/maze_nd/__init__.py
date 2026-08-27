"""Maze-ND substrate family container.

Exposes the authoritative ``substrate:maze-nd/v1`` definition object
(``MAZE_ND_DEFINITION``) at the discovery level, and the producer-owned
configuration surface (``resolve_configuration``, ``MazeNDConfiguration``,
``MazeNDConfigurationError``), planning resolver (``plan``), and execution
operation (``execute``) with their scientific owner. It also re-exports the
Maze-ND source/extraction/normalization/lineage building blocks so tests and
callers address them at the family boundary. This package only re-exports and
contains these; it defines no framework lifecycle semantics itself.
"""

from __future__ import annotations

from .configuration import (
    MazeNDConfiguration,
    MazeNDConfigurationError,
    resolve_configuration,
)
from .definition import MAZE_ND_DEFINITION
from .execution import MazeNDExecutionError, execute
from .extraction import (
    EXTRACTION_SCHEMA,
    ExtractedTopology,
    ExtractionError,
    extract_row,
)
from .lineage import (
    DEDUPLICATION_POLICY,
    LineageError,
    SourceOccurrenceIdentity,
    TopologyGroup,
    build_lineage_resource,
    group_source_occurrences,
    normalized_topology_key,
    occurrence_identity,
)
from .normalization import (
    NORMALIZATION_POLICY,
    NormalizationError,
    normalize,
)
from .planning import plan as plan
from .source import (
    FingerprintMismatchError,
    SourceError,
    content_fingerprint,
    load_source,
    verify_fingerprint,
)

__all__ = [
    "DEDUPLICATION_POLICY",
    "EXTRACTION_SCHEMA",
    "FingerprintMismatchError",
    "LineageError",
    "MAZE_ND_DEFINITION",
    "MazeNDConfiguration",
    "MazeNDConfigurationError",
    "MazeNDExecutionError",
    "NORMALIZATION_POLICY",
    "NormalizationError",
    "SourceError",
    "SourceOccurrenceIdentity",
    "TopologyGroup",
    "build_lineage_resource",
    "content_fingerprint",
    "execute",
    "extract_row",
    "ExtractedTopology",
    "ExtractionError",
    "group_source_occurrences",
    "load_source",
    "normalize",
    "normalized_topology_key",
    "occurrence_identity",
    "plan",
    "resolve_configuration",
    "verify_fingerprint",
]
