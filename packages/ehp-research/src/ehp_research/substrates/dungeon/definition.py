from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from ehp_sn import RasterTopology


@dataclass(frozen=True, slots=True, kw_only=True)
class DungeonDefinition:
    topology: RasterTopology
    metadata: Mapping[str, object]
