from __future__ import annotations

from ehp_sn import ContractRef, RasterTopology, RasterTopologyValidator, SpatialDomainValidator

MAZEND_OUTPUT_V1 = ContractRef(name="mazend-output", version=1)


class MazeNDOutputValidator:
    def validate(self, value: RasterTopology) -> None:
        SpatialDomainValidator().validate(value.domain)
        RasterTopologyValidator().validate(value)
