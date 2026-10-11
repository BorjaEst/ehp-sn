from __future__ import annotations

from ehp_sn import (
    ContractRef,
    ContractViolation,
    ObservationFieldValidator,
    RasterTopology,
    SpatialDomainValidator,
)

from .definition import ObsfieldDefinition
from .settings import ObsfieldSettings

OBSFIELD_V1 = ContractRef(name="obsfield", version=1)


class ObsfieldSettingsValidator:
    def validate(self, value: ObsfieldSettings) -> None:
        if not value.channels:
            raise ContractViolation(
                "obsfield must declare at least one channel",
                contract=OBSFIELD_V1,
                rule="obsfield.parameter.channels",
                subject="channels",
            )
        if not value.observation_model:
            raise ContractViolation(
                "obsfield must declare an observation model",
                contract=OBSFIELD_V1,
                rule="obsfield.parameter.observation_model",
                subject="observation_model",
            )


class ObsfieldScientificValidator:
    def validate(self, value: ObsfieldDefinition) -> None:
        SpatialDomainValidator().validate(value.domain)
        ObservationFieldValidator().validate(value.observations)
        if value.observations.domain != value.domain:
            raise ContractViolation(
                "the observation field must share the declared domain",
                contract=OBSFIELD_V1,
                rule="obsfield.content.domain",
            )


class ObsfieldTopologyCompatibilityValidator:
    def validate(self, value: tuple[RasterTopology, ObsfieldDefinition]) -> None:
        topology, observation = value
        if topology.domain.shape != observation.domain.shape:
            raise ContractViolation(
                "observation field domain must share the topology shape",
                contract=OBSFIELD_V1,
                rule="obsfield.compatibility.shape",
            )
        if topology.domain.coordinates != observation.domain.coordinates:
            raise ContractViolation(
                "observation field domain must share the topology coordinate system",
                contract=OBSFIELD_V1,
                rule="obsfield.compatibility.coordinates",
            )
