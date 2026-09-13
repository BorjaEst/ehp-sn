from __future__ import annotations

from dataclasses import dataclass

ROLE = "topology"


@dataclass(frozen=True)
class Topology:
    """Internal family root for topology contracts.

    It deliberately declares no movement or validation surface; each concrete
    topology contract owns its own authoritative structure.
    """


__all__ = ["ROLE", "Topology"]
