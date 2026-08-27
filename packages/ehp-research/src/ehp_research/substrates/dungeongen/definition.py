"""Authoritative DungeonGen v1 substrate definition.

This module is the single authoritative home of the
``substrate:dungeongen/v1`` definition object (``DUNGEONGEN_DEFINITION``) at
the discovery level in ``ehp_research``.

It carries only demonstrated discovery facts:

* canonical reference: ``substrate:dungeongen/v1``;
* a concise description of the substrate definition;
* the normalized output contract: ``raster-topology/v1``.

It deliberately carries no generation/acceptance/conversion configuration and
no planner/builder/execution hooks (those are planning-phase concerns in this
package). The scientific specification for DungeonGen v1 is
``docs/docs/research/substrates/dungeongen-v1.md``.
"""

from __future__ import annotations

from ehp_sn.experiments import ComponentRef

from .._definition import SubstrateDefinition

DUNGEONGEN_DEFINITION = SubstrateDefinition(
    ref=ComponentRef.parse("substrate:dungeongen/v1"),
    description=(
        "Reusable procedural irregular raster-topology substrate: normalized "
        "raster topologies generated from the frozen dungeongen production "
        "dependency and conforming to raster-topology/v1."
    ),
    output_contract="raster-topology/v1",
)

__all__ = ["DUNGEONGEN_DEFINITION"]
