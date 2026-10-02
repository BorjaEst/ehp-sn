from __future__ import annotations

from typing import TYPE_CHECKING

from ehp_sn.contracts.capabilities import raster_generator

from .configuration import Configuration, Parameters

if TYPE_CHECKING:
    from dungeongen.layout import DungeonGenerator, GenerationParams, OccupancyGrid

__all__ = ["Generator", "create", "to_provider_parameters"]


class Generator:
    """Adapts the external generator to the provider-independent capability.

    It translates representation only: it derives passability and a normalized
    extent. Scientific acceptance, retries, duplicate handling, and record
    selection remain the consuming substrate's responsibility.
    """

    def __init__(self, provider: DungeonGenerator) -> None:
        self._provider = provider

    def generate(self, *, seed: int) -> raster_generator.GeneratedRaster:
        # The upstream API exposes the raster on the generator after a run.
        self._provider.generate(seed=seed)
        return _to_generated_raster(self._provider.occupancy)


def create(config: Configuration) -> raster_generator.RasterGenerator:
    """Construct and adapt the provider from its bound configuration.

    The external import is local so the declaration is discoverable without
    eagerly loading the optional integration package.
    """
    from dungeongen.layout import DungeonGenerator

    return Generator(DungeonGenerator(to_provider_parameters(config.parameters)))


def to_provider_parameters(parameters: Parameters) -> GenerationParams:
    from dungeongen.layout import (
        DungeonArchetype,
        DungeonSize,
        GenerationParams,
        SymmetryType,
    )

    return GenerationParams(
        archetype=DungeonArchetype[parameters.archetype.upper()],
        size=DungeonSize[parameters.size.upper()],
        symmetry=SymmetryType[parameters.symmetry.upper()],
        room_size_bias=parameters.room_size_bias,
        round_room_chance=parameters.round_room_chance,
        hall_chance=parameters.hall_chance,
        density=parameters.density,
        symmetry_break=parameters.symmetry_break,
        linearity=parameters.linearity,
        loop_factor=parameters.loop_factor,
        passage_width=parameters.passage_width,
        winding=parameters.winding,
        extra_room_connections=parameters.extra_room_connections,
        extra_passage_junctions=parameters.extra_passage_junctions,
        levels=parameters.levels,
        stair_frequency=parameters.stair_frequency,
        water_enabled=parameters.water_enabled,
        water_threshold=parameters.water_threshold,
    )


def _to_generated_raster(occupancy: OccupancyGrid) -> raster_generator.GeneratedRaster:
    """Translate the provider's occupancy grid into a normalized raster.

    Passability is the provider's room and passage cells; the origin is
    normalized to the tight bounding box, because the provider's absolute
    coordinates carry no scientific meaning.
    """
    cells: set[tuple[int, int]] = set()
    for group in (occupancy.room_cells, occupancy.passage_cells):
        for group_cells in group.values():
            cells |= group_cells

    if not cells:
        return raster_generator.GeneratedRaster(width=0, height=0, passable=frozenset())

    xs = [x for x, _ in cells]
    ys = [y for _, y in cells]
    min_x, min_y = min(xs), min(ys)
    width = max(xs) - min_x + 1
    height = max(ys) - min_y + 1
    passable = frozenset((x - min_x, y - min_y) for x, y in cells)

    return raster_generator.GeneratedRaster(
        width=width,
        height=height,
        passable=passable,
    )
