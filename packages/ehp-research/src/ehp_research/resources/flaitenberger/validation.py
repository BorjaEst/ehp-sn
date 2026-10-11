from __future__ import annotations

from ehp_sn import ContractRef, RasterTopology, RasterTopologyValidator, SpatialDomainValidator

FLAITENBERGER_OUTPUT_V1 = ContractRef(name="flaitenberger-output", version=1)


class FlaitenbergerOutputValidator:
    def validate(self, value: RasterTopology) -> None:
        SpatialDomainValidator().validate(value.domain)
        RasterTopologyValidator().validate(value)
