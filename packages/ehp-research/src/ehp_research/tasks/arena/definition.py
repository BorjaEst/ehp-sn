from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import ObservationField, RasterTopology


@dataclass(frozen=True, slots=True, kw_only=True)
class ArenaTaskDefinition:
    topology: RasterTopology
    observations: ObservationField
