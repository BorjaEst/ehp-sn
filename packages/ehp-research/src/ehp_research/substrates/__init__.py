from __future__ import annotations

from .dagflow import DEFINITION as DAGFLOW
from .dungeongen import DEFINITION as DUNGEONGEN
from .mazend import DEFINITION as MAZEND
from .obsfield import DEFINITION as OBSFIELD

SUBSTRATE_DEFINITIONS = (DAGFLOW, DUNGEONGEN, MAZEND, OBSFIELD)

__all__ = [
    "DAGFLOW",
    "DUNGEONGEN",
    "MAZEND",
    "OBSFIELD",
    "SUBSTRATE_DEFINITIONS",
]
