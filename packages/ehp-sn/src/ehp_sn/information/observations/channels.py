from __future__ import annotations

from dataclasses import dataclass

from ...contracts.diagnostics import ContractViolation
from ...contracts.identity import ContractRef

OBSERVATION_SCHEMA_V1 = ContractRef(name="observation-schema", version=1)


@dataclass(frozen=True, slots=True, kw_only=True)
class ObservationChannel:
    name: str
    dtype: str
    shape: tuple[int, ...]
    role: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ObservationSchema:
    channels: tuple[ObservationChannel, ...]


class ObservationSchemaValidator:
    def validate(self, value: ObservationSchema) -> None:
        names = [channel.name for channel in value.channels]
        if not names:
            raise ContractViolation(
                "an observation schema must declare at least one channel",
                contract=OBSERVATION_SCHEMA_V1,
                rule="observation-schema.channels.empty",
            )
        if len(set(names)) != len(names):
            raise ContractViolation(
                "observation channel names must be unique",
                contract=OBSERVATION_SCHEMA_V1,
                rule="observation-schema.channels.unique",
            )
