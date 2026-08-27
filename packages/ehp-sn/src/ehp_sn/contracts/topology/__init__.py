"""Topology contracts (``ehp_sn`` framework-owned).

Subpackage re-exports the topology contract implementations, for example
:class:`~ehp_sn.contracts.topology.raster_topology.RasterTopology`. The
normative semantics live in ``docs/docs/framework/contracts/topology/``.
"""

from __future__ import annotations

from .raster_topology import (
    COORDINATE_SYSTEM,
    DIRECTED,
    EDGE_COST_KIND,
    MOVEMENT_KIND,
    MOVEMENT_LABELS,
    SCHEMA_REF,
    STAY_INCLUDED,
    TOPOLOGY_KIND,
    RasterTopology,
    RasterTopologyError,
    raster_topology,
)

__all__ = [
    "COORDINATE_SYSTEM",
    "DIRECTED",
    "EDGE_COST_KIND",
    "MOVEMENT_KIND",
    "MOVEMENT_LABELS",
    "RasterTopology",
    "RasterTopologyError",
    "SCHEMA_REF",
    "STAY_INCLUDED",
    "TOPOLOGY_KIND",
    "raster_topology",
]
