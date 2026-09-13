from __future__ import annotations

from dataclasses import dataclass

ROLE = "relations"


@dataclass(frozen=True)
class Relation:
    """Internal family root for relation contracts.

    It deliberately declares no relation payload; each concrete relation
    contract owns its own authoritative structure.
    """


__all__ = ["ROLE", "Relation"]
