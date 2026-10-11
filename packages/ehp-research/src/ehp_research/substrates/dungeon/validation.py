from __future__ import annotations

from ehp_sn import (
    ContractRef,
    ContractViolation,
    RasterTopologyValidator,
    SpatialDomainValidator,
)

from .definition import DungeonDefinition
from .settings import DungeonSettings

DUNGEON_V1 = ContractRef(name="dungeon", version=1)
SUPPORTED_DUPLICATE_POLICIES = frozenset({"reject", "allow"})


class DungeonSettingsValidator:
    def validate(self, value: DungeonSettings) -> None:
        if not value.generator:
            raise ContractViolation(
                "dungeon must declare a generator",
                contract=DUNGEON_V1,
                rule="dungeon.parameter.generator",
                subject="generator",
            )
        if value.record_count < 1:
            raise ContractViolation(
                "record_count must be at least 1",
                contract=DUNGEON_V1,
                rule="dungeon.parameter.record_count",
                subject="record_count",
            )
        if value.duplicate_policy not in SUPPORTED_DUPLICATE_POLICIES:
            raise ContractViolation(
                f"unsupported duplicate policy {value.duplicate_policy!r}",
                contract=DUNGEON_V1,
                rule="dungeon.parameter.duplicate_policy",
                subject=value.duplicate_policy,
            )


class DungeonScientificValidator:
    def validate(self, value: DungeonDefinition) -> None:
        SpatialDomainValidator().validate(value.topology.domain)
        RasterTopologyValidator().validate(value.topology)
