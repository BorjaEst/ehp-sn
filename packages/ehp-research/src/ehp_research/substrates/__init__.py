from __future__ import annotations

from .dagflow import DEFINITION as DAGFLOW
from .dungeon import DEFINITION as DUNGEON
from .mazend import DEFINITION as MAZEND
from .obsfield import DEFINITION as OBSFIELD

SUBSTRATE_DEFINITIONS = (DAGFLOW, DUNGEON, MAZEND, OBSFIELD)

__all__ = [
    "DAGFLOW",
    "DUNGEON",
    "MAZEND",
    "OBSFIELD",
    "SUBSTRATE_DEFINITIONS",
]
