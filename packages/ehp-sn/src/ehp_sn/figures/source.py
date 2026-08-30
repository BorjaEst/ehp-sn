"""Figure artifact-metadata surface vocabulary (Phase 5).

An artifact-scope figure consumes the committed artifact's collection of records
conforming to a declared logical contract. Most artifact-scope figures — the
generic contract-level artifact summaries — need only that record collection.

Some artifact-scope figures are producer-owned diagnostics (for example a
generation summary) that additionally consume the committed artifact's
producer-owned metadata: the artifact-level producer descriptors, its
provenance, and its auxiliary (non-record) logical resources. The framework
carries that metadata **opaquely** and never interprets a producer name or
value (``ARCH-001``); only the producer-owned ``FigureSpec`` in ``ehp_research``
interprets the descriptors it itself declared.

This module owns the generic surface vocabulary a figure may declare
(``producer-descriptors``, ``provenance``, ``auxiliary``) and the frozen
:class:`ArtifactSourceContent` handed to a figure's ``select``/``prepare`` when
it declares surfaces. It is a leaf module with no figure imports (mirrors
``scope.py``) so both ``contracts.py`` and ``service.py`` can consume it without
a circular dependency. It introduces no producer name and no producer identity
(Phase-5 § 22).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ehp_sn.artifacts.descriptors import ProducerDescriptor
from ehp_sn.execution import LogicalRecord, LogicalResource

#: Surface: the artifact-level producer-declared descriptors.
SURFACE_PRODUCER_DESCRIPTORS = "producer-descriptors"

#: Surface: the artifact provenance (build/identity provenance view).
SURFACE_PROVENANCE = "provenance"

#: Surface: the artifact's auxiliary (non-record) logical resources.
SURFACE_AUXILIARY = "auxiliary"

#: The ordinary artifact-metadata surface vocabulary an artifact-scope figure
#: may declare. A figure never invents a surface name; an unknown name is
#: rejected at requirement construction (Phase-5 · P5-SURF).
ARTIFACT_METADATA_SURFACES: frozenset[str] = frozenset(
    {SURFACE_PRODUCER_DESCRIPTORS, SURFACE_PROVENANCE, SURFACE_AUXILIARY}
)


@dataclass(frozen=True, slots=True)
class ArtifactSourceContent:
    """Artifact-scope source content handed to a figure declaring metadata surfaces.

    ``records`` is the contract-conforming record collection (the same content
    the generic artifact summaries consume). Each metadata field is populated
    only for a declared surface and is carried **exactly as resolved** from the
    committed artifact — the framework never interprets, filters, or aggregates
    a producer value by name. A field for an undeclared surface is its empty or
    absent default.

    This is a framework-admitted stable point-in-time representation bound to
    the immutable committed release (``ART-001``/``DATA-006``); it is not a
    producer-specific source type (``projection.md`` § "Source roles").
    """

    records: tuple[LogicalRecord, ...]
    producer_descriptors: tuple[ProducerDescriptor, ...] = ()
    provenance: dict[str, Any] | None = None
    auxiliary: tuple[LogicalResource, ...] = ()


__all__ = [
    "ARTIFACT_METADATA_SURFACES",
    "ArtifactSourceContent",
    "SURFACE_AUXILIARY",
    "SURFACE_PRODUCER_DESCRIPTORS",
    "SURFACE_PROVENANCE",
]
