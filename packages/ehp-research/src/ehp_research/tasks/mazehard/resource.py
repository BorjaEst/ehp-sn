from __future__ import annotations

from typing import Protocol, runtime_checkable

from ehp_sn import RasterTopology


@runtime_checkable
class MazeHardMazeSource(Protocol):
    def generate(self, *, seed: int) -> RasterTopology: ...
