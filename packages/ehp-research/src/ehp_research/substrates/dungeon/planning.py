from __future__ import annotations

from ehp_sn import planning
from ehp_sn.contracts.capabilities.raster_generator import RasterGenerator

from .configuration import Configuration


def create(
    config: Configuration,
    *,
    generator: RasterGenerator,
) -> planning.PlanningDeclaration: ...


__all__ = ["create"]
