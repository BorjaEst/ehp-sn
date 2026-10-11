from __future__ import annotations

from ehp_sn import ContractRef, ContractViolation

from .definition import MazeHardTaskDefinition
from .settings import MazeHardSettings

MAZEHARD_V1 = ContractRef(name="mazehard", version=1)


class MazeHardSettingsValidator:
    def validate(self, value: MazeHardSettings) -> None:
        if not value.difficulty:
            raise ContractViolation(
                "mazehard must declare a difficulty",
                contract=MAZEHARD_V1,
                rule="mazehard.parameter.difficulty",
                subject="difficulty",
            )
        if value.sequence_length < 1:
            raise ContractViolation(
                "sequence_length must be at least 1",
                contract=MAZEHARD_V1,
                rule="mazehard.parameter.sequence_length",
                subject="sequence_length",
            )
        if not value.encoding:
            raise ContractViolation(
                "mazehard must declare an encoding",
                contract=MAZEHARD_V1,
                rule="mazehard.parameter.encoding",
                subject="encoding",
            )


class MazeHardPathValidator:
    def validate(self, value: tuple[MazeHardTaskDefinition, tuple[tuple[float, ...], ...]]) -> None:
        task, path = value
        shape = task.topology.domain.shape
        if not path:
            raise ContractViolation(
                "a reference path must contain at least one position",
                contract=MAZEHARD_V1,
                rule="mazehard.path.empty",
            )
        for index, position in enumerate(path):
            if len(position) != len(shape):
                raise ContractViolation(
                    "path positions must match the topology rank",
                    contract=MAZEHARD_V1,
                    rule="mazehard.path.rank",
                    subject=str(index),
                )
            for coordinate, extent in zip(position, shape, strict=True):
                if not 0 <= coordinate < extent:
                    raise ContractViolation(
                        "path positions must remain within the topology extent",
                        contract=MAZEHARD_V1,
                        rule="mazehard.path.bounds",
                        subject=str(index),
                    )


class MazeHardDatasetValidator:
    def validate(self, value: object) -> None:
        if not hasattr(value, "__len__"):
            raise ContractViolation(
                "a mazehard dataset must be indexable",
                contract=MAZEHARD_V1,
                rule="mazehard.dataset.indexed",
            )
