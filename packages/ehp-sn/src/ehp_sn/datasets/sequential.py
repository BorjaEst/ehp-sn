from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ..contracts.diagnostics import ContractViolation
from ..contracts.identity import ContractRef
from ..information.observations.channels import ObservationSchema
from ..information.temporal.alignment import TransitionAlignment

SEQUENTIAL_EPISODES_V1 = ContractRef(name="sequential-episodes", version=1)


@runtime_checkable
class SequentialDataset[T](Protocol):
    def episodes(self) -> Iterable[Sequence[T]]: ...


@dataclass(frozen=True, slots=True, kw_only=True)
class SequentialDatasetDefinition:
    alignment: TransitionAlignment
    observations: ObservationSchema


class SequentialDatasetValidator:
    def validate(self, value: SequentialDataset[object]) -> None:
        for index, episode in enumerate(value.episodes()):
            if len(episode) < 2:
                raise ContractViolation(
                    "an episode must contain at least two steps",
                    contract=SEQUENTIAL_EPISODES_V1,
                    rule="sequential-episodes.episode.length",
                    subject=str(index),
                )
