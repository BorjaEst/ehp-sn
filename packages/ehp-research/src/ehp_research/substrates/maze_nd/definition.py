"""Authoritative Maze-ND v1 substrate definition.

This module is the single authoritative home of the ``substrate:maze-nd/v1``
definition object (``MAZE_ND_DEFINITION``) at the discovery level in
``ehp_research``.

It carries only demonstrated discovery facts:

* canonical reference: ``substrate:maze-nd/v1``;
* a concise description of the substrate definition;
* the normalized output contract: ``raster-topology/v1``.

It deliberately carries no source/selection/normalization configuration and no
planner/builder/execution hooks (those are planning-phase concerns, and several
are explicitly unresolved in the Maze-ND specification). The scientific
specification for Maze-ND v1 is
``docs/docs/research/substrates/maze-nd-v1.md``.
"""

from __future__ import annotations

from ehp_sn.experiments import ComponentRef

from .._definition import SubstrateDefinition

MAZE_ND_DEFINITION = SubstrateDefinition(
    ref=ComponentRef.parse("substrate:maze-nd/v1"),
    description=(
        "Reusable raster maze-topology substrate: normalized raster "
        "topologies extracted from an authoritative external source and "
        "conforming to raster-topology/v1."
    ),
    output_contract="raster-topology/v1",
)

__all__ = ["MAZE_ND_DEFINITION"]
