from __future__ import annotations

from ehp_sn import RasterTopology


class DungeonTopologyAdapter:
    def to_contract(self, value: RasterTopology) -> RasterTopology:
        return value
