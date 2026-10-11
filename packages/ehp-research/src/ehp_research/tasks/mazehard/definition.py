from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import RasterTopology, SpatialPosition


@dataclass(frozen=True, slots=True, kw_only=True)
class MazeHardTaskDefinition:
    topology: RasterTopology
    start: SpatialPosition
    goal: SpatialPosition
