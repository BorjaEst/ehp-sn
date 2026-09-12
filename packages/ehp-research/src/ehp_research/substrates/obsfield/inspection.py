from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import substrates
from ehp_sn.contracts.data.structures.observations import categorical_field
from ehp_sn.contracts.data.structures.observations.categorical_field import Artifact

from .configuration import Configuration


@dataclass(frozen=True)
class SummaryResult(substrates.SummaryResult): ...


@dataclass(frozen=True)
class InspectResult(substrates.InspectResult): ...


def summarize(artifact: Artifact) -> SummaryResult:
    """Describe the committed field as a whole. Read-only."""
    counts = _observation_counts(artifact)
    return SummaryResult(
        record_count=len(artifact.records),
        facts=(
            ("distinct_observation_ids", len(counts)),
            ("most_frequent_observation_ids", _most_frequent_identifiers(counts)),
        ),
    )


def inspect(artifact: Artifact, record_id: str) -> InspectResult:
    """Expose the substrate-specific information of exactly one record."""
    record = _find_record(artifact, record_id)
    return InspectResult(record_id=record_id, fields=_record_facts(record))


def _observation_counts(artifact: Artifact) -> dict[int, int]:
    """How often each vocabulary entry occurs across the whole artifact."""
    ...


def _most_frequent_identifiers(counts: dict[int, int]) -> tuple[int, ...]:
    """Vocabulary entries ordered by descending frequency."""
    ...


def _find_record(artifact: Artifact, record_id: str) -> categorical_field.CategoricalField:
    """Resolve one record by its stable identity, never by position."""
    ...


def _record_facts(record: categorical_field.CategoricalField) -> tuple[tuple[str, object], ...]:
    """Substrate-specific inspection facts for one record."""
    ...


__all__ = ["InspectResult", "SummaryResult", "inspect", "summarize"]
