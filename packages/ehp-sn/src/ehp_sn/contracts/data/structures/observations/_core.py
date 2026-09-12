import dataclasses
from collections.abc import Sequence

ROLE = "observations"


class ObservationsError(ValueError):
    pass


@dataclasses.dataclass(frozen=True)
class Vocabulary:
    identity: str
    cardinality: int


@dataclasses.dataclass(frozen=True)
class Observations:
    vocabulary: Vocabulary
    observation_id: Sequence[int]


__all__ = ["ROLE", "Observations", "ObservationsError", "Vocabulary"]
