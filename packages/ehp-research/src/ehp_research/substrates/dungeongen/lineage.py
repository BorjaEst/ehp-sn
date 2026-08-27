"""DungeonGen production lineage.

This module owns the producer lineage recorded for each accepted topology record
and the complete per-index rejection/lineage logical resource. The lineage
establishes, for each record:

* logical topology index;
* accepted attempt index;
* generator dependency;
* generator protocol;
* generator profile;
* conversion policy;
* component-selection policy;
* acceptance policy;
* duplicate policy.

The accepted-attempt index belongs in lineage/descriptors, **not** in the common
``raster-topology/v1`` payload (the specification is explicit on this boundary).
Generator-internal room numbers and upstream object IDs are never exposed as
ordinary scientific channels.
"""

from __future__ import annotations

from typing import Any

from ._dependency import (
    ACCEPTANCE_POLICY,
    COMPONENT_SELECTION_POLICY,
    CONVERSION_POLICY,
    DEPENDENCY_REFERENCE,
    LINEAGE_SCHEMA,
    PROFILE_REFERENCE,
    PROTOCOL_REFERENCE,
    RANDOMNESS_ROLE,
)
from .acceptance import AcceptedTopology

#: Canonical name of the complete DungeonGen lineage logical resource.
LINEAGE_RESOURCE_NAME: str = "dungeongen-lineage"


def record_lineage(accepted: AcceptedTopology, *, record_id: str) -> dict[str, Any]:
    """Return the bounded JSON-compatible per-record lineage summary.

    Carries the logical index, accepted attempt, dependency/protocol/profile,
    conversion/component/acceptance/duplicate policy references, the randomness
    role, and the list of prior rejected attempts with reasons. This is bounded
    per record and kept out of the common raster payload.
    """
    return {
        "record_id": record_id,
        "logical_index": accepted.logical_index,
        "accepted_attempt": accepted.attempt,
        "generator_dependency": DEPENDENCY_REFERENCE,
        "generator_protocol": PROTOCOL_REFERENCE,
        "generator_profile": PROFILE_REFERENCE,
        "conversion_policy": CONVERSION_POLICY,
        "component_selection_policy": COMPONENT_SELECTION_POLICY,
        "acceptance_policy": ACCEPTANCE_POLICY,
        "duplicate_policy": "allow",
        "randomness_role": RANDOMNESS_ROLE,
        "rejections": [{"attempt": r.attempt, "reason": r.reason} for r in accepted.rejections],
    }


def build_lineage_resource(
    accepted: tuple[AcceptedTopology, ...],
    record_ids: dict[tuple[int, int, tuple[bool, ...]], str],
    *,
    duplicate_policy: str,
    seed: int,
    duplicate_reports: tuple[tuple[int, int, int, int], ...] = (),
) -> dict[str, Any]:
    """Build the complete DungeonGen lineage resource (Targets 11, 15).

    ``accepted`` is the ordered accepted realizations in logical-index order;
    ``record_ids`` maps each canonical topology key to its framework-derived
    ``record_id``. ``rejections_by_index`` lists, per logical index, the
    rejected attempts. Under ``allow`` the resource reports any detected exact
    duplicate content (canonical extent + passability) as
    ``(first_index, later_index, height, width)`` tuples without collapsing the
    records.
    """
    realizations: list[dict[str, Any]] = []
    for a in accepted:
        record_id = record_ids[(a.height, a.width, a.passable)]
        realizations.append(record_lineage(a, record_id=record_id))

    return {
        "resource": LINEAGE_RESOURCE_NAME,
        "schema": LINEAGE_SCHEMA,
        "generator_dependency": DEPENDENCY_REFERENCE,
        "generator_protocol": PROTOCOL_REFERENCE,
        "generator_profile": PROFILE_REFERENCE,
        "conversion_policy": CONVERSION_POLICY,
        "component_selection_policy": COMPONENT_SELECTION_POLICY,
        "acceptance_policy": ACCEPTANCE_POLICY,
        "duplicate_policy": duplicate_policy,
        "base_seed": seed,
        "randomness_role": RANDOMNESS_ROLE,
        "realizations": realizations,
        "duplicate_exact_reports": [
            {
                "first_logical_index": a,
                "later_logical_index": b,
                "height": h,
                "width": w,
            }
            for (a, b, h, w) in duplicate_reports
        ],
    }


__all__ = [
    "LINEAGE_RESOURCE_NAME",
    "build_lineage_resource",
    "record_lineage",
]
