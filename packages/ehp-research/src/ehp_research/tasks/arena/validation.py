from __future__ import annotations

from ehp_sn import (
    ContractRef,
    ContractViolation,
    EpisodeRecord,
    EpisodeValidator,
    ObservationField,
    RasterTopology,
)

from .settings import ArenaSettings

ARENA_V1 = ContractRef(name="arena", version=1)


class ArenaSettingsValidator:
    def validate(self, value: ArenaSettings) -> None:
        if value.horizon < 1:
            raise ContractViolation(
                "horizon must be at least 1",
                contract=ARENA_V1,
                rule="arena.parameter.horizon",
                subject="horizon",
            )
        if not value.observation_mode:
            raise ContractViolation(
                "arena must declare an observation mode",
                contract=ARENA_V1,
                rule="arena.parameter.observation_mode",
                subject="observation_mode",
            )
        if not value.action_mode:
            raise ContractViolation(
                "arena must declare an action mode",
                contract=ARENA_V1,
                rule="arena.parameter.action_mode",
                subject="action_mode",
            )


class ArenaEpisodeValidator:
    def validate(self, value: EpisodeRecord) -> None:
        EpisodeValidator().validate(value)


class ArenaInputCompatibilityValidator:
    def validate(self, value: tuple[RasterTopology, ObservationField]) -> None:
        topology, observations = value
        if topology.domain.shape != observations.domain.shape:
            raise ContractViolation(
                "observation field must share the topology shape",
                contract=ARENA_V1,
                rule="arena.compatibility.shape",
            )
        if topology.domain.coordinates != observations.domain.coordinates:
            raise ContractViolation(
                "observation field must share the topology coordinate system",
                contract=ARENA_V1,
                rule="arena.compatibility.coordinates",
            )
