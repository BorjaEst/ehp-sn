from __future__ import annotations

from ehp_sn import RasterTopology


class MazeNDAdapter:
    def generate(self, *, dimensions: tuple[int, ...], seed: int) -> RasterTopology:
        raise NotImplementedError("mazend generation requires the external generator implementation")
