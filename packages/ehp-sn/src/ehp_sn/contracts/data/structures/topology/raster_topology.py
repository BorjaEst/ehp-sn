from __future__ import annotations

from dataclasses import dataclass

from ehp_sn.contracts.data.structures.domains import rectangular_grid

from . import _core

SCHEMA_REF = "raster-topology"
V1 = f"{SCHEMA_REF}/v1"


@dataclass(frozen=True)
class RasterTopology(_core.Topology):
    """A `raster-topology/v1` movement structure over a rectangular domain.

    The domain is deliberately concrete: `raster-topology/v1` is specified
    over `rectangular-grid/v1`, so this field must not widen to the public
    domain union. `raster-topology/v1` is the only currently supported raster
    topology shape.
    """

    record_id: str
    domain: rectangular_grid.RectangularDomain


@dataclass(frozen=True)
class Artifact: ...


__all__ = ["Artifact", "SCHEMA_REF", "V1", "RasterTopology"]
