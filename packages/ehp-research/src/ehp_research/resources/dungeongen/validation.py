from __future__ import annotations

from ehp_sn import ContractRef, RasterTopology, RasterTopologyValidator, SpatialDomainValidator

DUNGEONGEN_OUTPUT_V1 = ContractRef(name="dungeongen-output", version=1)


class DungeonGenOutputValidator:
    def validate(self, value: RasterTopology) -> None:
        SpatialDomainValidator().validate(value.domain)
        RasterTopologyValidator().validate(value)
