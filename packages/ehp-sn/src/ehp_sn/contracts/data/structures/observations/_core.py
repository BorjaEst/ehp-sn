from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

ROLE = "observations"


class ObservationsError(ValueError):
    pass


@dataclass(frozen=True)
class Vocabulary:
    identity: str
    cardinality: int


@dataclass(frozen=True)
class Observations:
    """Internal family root for observation contracts.

    It holds the record content shared by observation contracts. It
    deliberately declares no ambient-domain field: not every observation
    contract is defined over a domain, so domain composition belongs to the
    concrete contract that needs it (see `categorical_field`).
    """

    vocabulary: Vocabulary
    observation_id: Sequence[int]


__all__ = ["ROLE", "Observations", "ObservationsError", "Vocabulary"]
