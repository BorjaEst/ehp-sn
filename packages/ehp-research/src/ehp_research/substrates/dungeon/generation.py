from __future__ import annotations

from ehp_sn import substrates
from ehp_sn.contracts.capabilities.raster_generator import RasterGenerator
from ehp_sn.contracts.data.structures.topology import raster_topology

from .configuration import Configuration


def generate(
    config: Configuration,
    *,
    generator: RasterGenerator,
) -> substrates.BuildResult[raster_topology.Artifact]: ...


__all__ = ["generate"]
