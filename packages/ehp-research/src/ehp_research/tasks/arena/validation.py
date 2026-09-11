from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import tasks
from ehp_sn.contracts.data.datasets.sequences import sequence_dataset
from ehp_sn.contracts.data.datasets.sequences.sequence_dataset import Artifact

from .configuration import Configuration


@dataclass(frozen=True)
class ValidationLevel(tasks.ValidationLevel): ...


@dataclass(frozen=True)
class ValidateResult(tasks.ValidateResult): ...


def validate(artifact: Artifact, level: ValidationLevel) -> ValidateResult: ...


__all__ = ["validate", "ValidationLevel", "ValidateResult"]
