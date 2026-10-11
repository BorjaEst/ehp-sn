from __future__ import annotations

from ehp_sn import RasterTopology


class DungeonGenAdapter:
    def generate(self, *, seed: int) -> RasterTopology:
        raise NotImplementedError("dungeongen generation requires the external generator implementation")
