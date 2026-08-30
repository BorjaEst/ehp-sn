"""Framework-owned release qualification status and inspection-review record (Phase 5).

Phase 5 § 36-43 attach an auditable **inspection-review record** and an explicit
per-release **qualification status** (``ACCEPTED`` / ``PROVISIONALLY_ACCEPTED``
/ ``BLOCKED``) to the exact committed artifact/release identity. This is
release/QA evidence — it is not a ``FigureArtifact`` and not part of
``ehp_sn.figures``.

This module is generic and producer-blind (``ARCH-001``). It models the
qualification **status vocabulary** and the **review record** shape, but applies
no acceptance judgement: validation/data-quality machinery establishes evidence,
producer figures expose it, and this module only records outcomes and resolves
the § 43 status-precedence rule. It never branches on a producer or contract
identity and contains no producer name.

## Status precedence (Phase 5 § 43)

``qualify`` resolves a per-release status from a collection of gate statuses and
one inspection-review record under these rules, in order:

1. an unresolved review anomaly (see :func:`unresolved_anomalies`) precludes
   ``ACCEPTED``/``PROVISIONALLY_ACCEPTED`` and therefore yields ``BLOCKED``;
2. any gate that is ``BLOCKED`` yields ``BLOCKED``;
3. otherwise, when a normative dependency is unresolved (passed explicitly as a
   boolean — no specific specification's status is hardcoded here), the status is
   ``PROVISIONALLY_ACCEPTED``;
4. otherwise the status is ``ACCEPTED``.

The record keeps the provenance-independent shape minimal and JSON-safe: enums
carry string values, identity collections are tuples of strings, and
:meth:`InspectionReviewRecord.to_dict` yields a plain JSON-serializable mapping.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class QualificationStatus(StrEnum):
    """The auditable qualification status of one committed artifact/release.

    ``ACCEPTED`` — full qualification; ``PROVISIONALLY_ACCEPTED`` — qualified
    pending resolution of an explicitly declared normative dependency;
    ``BLOCKED`` — not qualified (a gate failed, or an unresolved review anomaly
    remains).
    """

    ACCEPTED = "accepted"
    PROVISIONALLY_ACCEPTED = "provisionally_accepted"
    BLOCKED = "blocked"


class ReviewOutcome(StrEnum):
    """The overall outcome of one inspection review pass."""

    PASS = "pass"
    ANOMALY = "anomaly"
    NOT_APPLICABLE = "not_applicable"


class AnomalyDisposition(StrEnum):
    """How a recorded review anomaly was dispositioned.

    ``FALSE_POSITIVE`` and ``EXPECTED_BEHAVIOR`` resolve a finding; the others
    leave it unresolved and block an accepted qualification.
    """

    CONFIRMED_DEFECT = "confirmed_defect"
    FALSE_POSITIVE = "false_positive"
    EXPECTED_BEHAVIOR = "expected_behavior"
    SPECIFICATION_ISSUE = "specification_issue"
    FOLLOW_UP_REQUIRED = "follow_up_required"


#: Anomaly dispositions that resolve a finding and therefore do not block
#: qualification. A confirmed defect, specification issue, or follow-up
#: requirement remains unresolved and precludes an accepted status.
_RESOLVED_DISPOSITIONS: frozenset[AnomalyDisposition] = frozenset(
    {AnomalyDisposition.FALSE_POSITIVE, AnomalyDisposition.EXPECTED_BEHAVIOR}
)


@dataclass(frozen=True, slots=True)
class ReviewAnomaly:
    """One recorded finding from an inspection review."""

    description: str
    projection_identity: str
    disposition: AnomalyDisposition

    def to_dict(self) -> dict[str, str]:
        """Return the JSON-serializable mapping for this anomaly."""
        return {
            "description": self.description,
            "projection_identity": self.projection_identity,
            "disposition": self.disposition.value,
        }


@dataclass(frozen=True, slots=True)
class InspectionReviewRecord:
    """The auditable inspection-review record bound to one committed release.

    Records the exact committed artifact/release identity, the figure and
    projection identities inspected, the authored selection and its resolved
    selected record ids, and the review outcome with any recorded anomalies.
    Carries no acceptance judgement; the status is resolved separately by
    :func:`qualify`.
    """

    artifact_ref: str
    release_coordinate: str
    figure_spec_identities: tuple[str, ...] = ()
    projection_identities: tuple[str, ...] = ()
    authored_selection: str = ""
    resolved_selected_record_ids: tuple[str, ...] = ()
    review_outcome: ReviewOutcome = ReviewOutcome.NOT_APPLICABLE
    anomalies: tuple[ReviewAnomaly, ...] = ()
    review_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain JSON-serializable mapping of this record."""
        return {
            "artifact_ref": self.artifact_ref,
            "release_coordinate": self.release_coordinate,
            "figure_spec_identities": list(self.figure_spec_identities),
            "projection_identities": list(self.projection_identities),
            "authored_selection": self.authored_selection,
            "resolved_selected_record_ids": list(self.resolved_selected_record_ids),
            "review_outcome": self.review_outcome.value,
            "anomalies": [anomaly.to_dict() for anomaly in self.anomalies],
            "review_metadata": self.review_metadata,
        }


def unresolved_anomalies(review: InspectionReviewRecord) -> tuple[ReviewAnomaly, ...]:
    """Return the anomalies that remain unresolved for qualification.

    An anomaly is resolved when its disposition is ``FALSE_POSITIVE`` or
    ``EXPECTED_BEHAVIOR``. Any other recorded anomaly remains unresolved and
    precludes an accepted status (Phase 5 § 43).
    """
    return tuple(
        anomaly for anomaly in review.anomalies if anomaly.disposition not in _RESOLVED_DISPOSITIONS
    )


def qualify(
    statuses: tuple[QualificationStatus, ...],
    review: InspectionReviewRecord,
    normative_dependency_unresolved: bool = False,
) -> QualificationStatus:
    """Resolve the per-release qualification status (Phase 5 § 43 precedence).

    An unresolved review anomaly blocks regardless of the gate statuses. Any
    ``BLOCKED`` gate blocks. Otherwise a normative dependency that is unresolved
    yields ``PROVISIONALLY_ACCEPTED``; with none, the status is ``ACCEPTED``.

    ``normative_dependency_unresolved`` is an explicit input — this module never
    hardcodes the status of any specific specification.
    """
    if unresolved_anomalies(review):
        return QualificationStatus.BLOCKED
    if any(status == QualificationStatus.BLOCKED for status in statuses):
        return QualificationStatus.BLOCKED
    if normative_dependency_unresolved:
        return QualificationStatus.PROVISIONALLY_ACCEPTED
    return QualificationStatus.ACCEPTED


def review_record_to_json(review: InspectionReviewRecord) -> str:
    """Serialize an inspection-review record to a JSON string.

    Python's :mod:`json` does not encode dataclasses natively; ``to_dict``
    yields the JSON-safe mapping this helper encodes.
    """
    return json.dumps(review.to_dict(), sort_keys=True, indent=2)


__all__ = [
    "AnomalyDisposition",
    "InspectionReviewRecord",
    "QualificationStatus",
    "ReviewAnomaly",
    "ReviewOutcome",
    "qualify",
    "review_record_to_json",
    "unresolved_anomalies",
]
