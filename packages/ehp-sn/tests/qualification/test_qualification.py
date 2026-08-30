"""Tests for the framework qualification status and inspection-review record.

These exercise the ``ehp_sn.qualification`` vocabulary and the Phase 5 § 43
status-precedence rule:

* Q-ENUM — the status and disposition enums expose the exact documented values;
* Q-PREC — ``qualify`` precedence: any ``BLOCKED`` gate yields ``BLOCKED``;
  an unresolved normative dependency yields ``PROVISIONALLY_ACCEPTED`` only when
  no gate is ``BLOCKED``; otherwise the status is ``ACCEPTED``;
* Q-ANOM — an unresolved review anomaly precludes an accepted status, while
  resolved (false-positive / expected-behaviour) anomalies do not;
* Q-JSON — the review record serializes to JSON (via ``to_dict``) with the
  expected values;
* Q-FROZEN — the record and anomaly dataclasses are immutable (frozen).

The module is producer-blind: no producer or contract name appears.
"""

from __future__ import annotations

import json
from dataclasses import FrozenInstanceError

import pytest
from ehp_sn.qualification import (
    AnomalyDisposition,
    InspectionReviewRecord,
    QualificationStatus,
    ReviewAnomaly,
    ReviewOutcome,
    qualify,
    review_record_to_json,
    unresolved_anomalies,
)


def _review(
    *,
    outcome: ReviewOutcome = ReviewOutcome.PASS,
    anomalies: tuple[ReviewAnomaly, ...] = (),
) -> InspectionReviewRecord:
    return InspectionReviewRecord(
        artifact_ref="artifact:example/v1",
        release_coordinate="stage-e/v1",
        figure_spec_identities=("figure:example-summary/v1",),
        projection_identities=("sha256:proj",),
        authored_selection="example-selection",
        resolved_selected_record_ids=("sha256:rec-0",),
        review_outcome=outcome,
        anomalies=anomalies,
        review_metadata={"inspector": "reviewer"},
    )


# ---------------------------------------------------------------------------
# Q-ENUM — enum values
# ---------------------------------------------------------------------------


def test_qualification_status_values() -> None:
    assert [e.value for e in QualificationStatus] == [
        "accepted",
        "provisionally_accepted",
        "blocked",
    ]


def test_review_outcome_values() -> None:
    assert [e.value for e in ReviewOutcome] == ["pass", "anomaly", "not_applicable"]


def test_anomaly_disposition_values() -> None:
    assert [e.value for e in AnomalyDisposition] == [
        "confirmed_defect",
        "false_positive",
        "expected_behavior",
        "specification_issue",
        "follow_up_required",
    ]


# ---------------------------------------------------------------------------
# Q-PREC — qualify precedence
# ---------------------------------------------------------------------------


def test_all_accepted_is_accepted() -> None:
    assert (
        qualify(
            (QualificationStatus.ACCEPTED, QualificationStatus.ACCEPTED),
            _review(),
        )
        == QualificationStatus.ACCEPTED
    )


def test_any_blocked_gate_is_blocked() -> None:
    assert (
        qualify(
            (QualificationStatus.ACCEPTED, QualificationStatus.BLOCKED),
            _review(),
        )
        == QualificationStatus.BLOCKED
    )
    assert (
        qualify(
            (QualificationStatus.BLOCKED,),
            _review(),
        )
        == QualificationStatus.BLOCKED
    )


def test_unresolved_dependency_is_provisionally_accepted_when_no_blocked() -> None:
    assert (
        qualify(
            (QualificationStatus.ACCEPTED,),
            _review(),
            normative_dependency_unresolved=True,
        )
        == QualificationStatus.PROVISIONALLY_ACCEPTED
    )


def test_blocked_gate_beats_unresolved_dependency() -> None:
    assert (
        qualify(
            (QualificationStatus.BLOCKED,),
            _review(),
            normative_dependency_unresolved=True,
        )
        == QualificationStatus.BLOCKED
    )


def test_no_unresolved_dependency_is_accepted() -> None:
    assert (
        qualify(
            (QualificationStatus.ACCEPTED,),
            _review(),
            normative_dependency_unresolved=False,
        )
        == QualificationStatus.ACCEPTED
    )


# ---------------------------------------------------------------------------
# Q-ANOM — unresolved review anomaly blocks qualification
# ---------------------------------------------------------------------------


def test_unresolved_anomaly_blocks() -> None:
    review = _review(
        outcome=ReviewOutcome.ANOMALY,
        anomalies=(
            ReviewAnomaly(
                description="dimension mismatch",
                projection_identity="sha256:proj",
                disposition=AnomalyDisposition.CONFIRMED_DEFECT,
            ),
        ),
    )
    assert unresolved_anomalies(review) == review.anomalies
    assert qualify((QualificationStatus.ACCEPTED,), review) == QualificationStatus.BLOCKED


def test_unresolved_anomaly_beats_otherwise_accepted_gates() -> None:
    review = _review(
        outcome=ReviewOutcome.ANOMALY,
        anomalies=(
            ReviewAnomaly(
                description="pending follow-up",
                projection_identity="sha256:proj",
                disposition=AnomalyDisposition.FOLLOW_UP_REQUIRED,
            ),
        ),
    )
    assert (
        qualify(
            (QualificationStatus.ACCEPTED, QualificationStatus.PROVISIONALLY_ACCEPTED),
            review,
        )
        == QualificationStatus.BLOCKED
    )


def test_resolved_anomalies_do_not_block() -> None:
    review = _review(
        outcome=ReviewOutcome.ANOMALY,
        anomalies=(
            ReviewAnomaly(
                description="explained rendering",
                projection_identity="sha256:proj",
                disposition=AnomalyDisposition.FALSE_POSITIVE,
            ),
            ReviewAnomaly(
                description="documented behaviour",
                projection_identity="sha256:proj",
                disposition=AnomalyDisposition.EXPECTED_BEHAVIOR,
            ),
        ),
    )
    assert unresolved_anomalies(review) == ()
    assert qualify((QualificationStatus.ACCEPTED,), review) == QualificationStatus.ACCEPTED


def test_empty_anomalies_do_not_block() -> None:
    assert unresolved_anomalies(_review()) == ()


# ---------------------------------------------------------------------------
# Q-JSON — record serializes to JSON
# ---------------------------------------------------------------------------


def test_record_to_dict_is_json_serializable() -> None:
    review = _review(
        outcome=ReviewOutcome.ANOMALY,
        anomalies=(
            ReviewAnomaly(
                description="mismatch",
                projection_identity="sha256:proj",
                disposition=AnomalyDisposition.CONFIRMED_DEFECT,
            ),
        ),
    )
    payload = review.to_dict()
    assert json.dumps(payload, sort_keys=True)  # no raise; values are JSON-safe
    assert payload["artifact_ref"] == "artifact:example/v1"
    assert payload["release_coordinate"] == "stage-e/v1"
    assert payload["figure_spec_identities"] == ["figure:example-summary/v1"]
    assert payload["projection_identities"] == ["sha256:proj"]
    assert payload["authored_selection"] == "example-selection"
    assert payload["resolved_selected_record_ids"] == ["sha256:rec-0"]
    assert payload["review_outcome"] == "anomaly"
    assert payload["anomalies"][0]["disposition"] == "confirmed_defect"
    assert payload["review_metadata"] == {"inspector": "reviewer"}


def test_review_record_to_json_roundtrip() -> None:
    review = _review()
    rendered = review_record_to_json(review)
    parsed = json.loads(rendered)
    assert parsed["artifact_ref"] == "artifact:example/v1"
    assert parsed["review_outcome"] == "pass"


def test_enum_values_are_json_native() -> None:
    assert json.dumps({"status": QualificationStatus.BLOCKED.value}) == ('{"status": "blocked"}')


# ---------------------------------------------------------------------------
# Q-FROZEN — records and anomalies are immutable
# ---------------------------------------------------------------------------


def test_inspection_review_record_is_frozen() -> None:
    review = _review()
    with pytest.raises(FrozenInstanceError):
        review.artifact_ref = "artifact:other/v1"  # type: ignore[misc]


def test_review_anomaly_is_frozen() -> None:
    anomaly = ReviewAnomaly(
        description="x",
        projection_identity="p",
        disposition=AnomalyDisposition.CONFIRMED_DEFECT,
    )
    with pytest.raises(FrozenInstanceError):
        anomaly.description = "y"  # type: ignore[misc]
