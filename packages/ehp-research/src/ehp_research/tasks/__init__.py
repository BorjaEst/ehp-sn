from __future__ import annotations

from .arena import DEFINITION as ARENA
from .mazehard import DEFINITION as MAZEHARD
from .prospect import DEFINITION as PROSPECT
from .routebind import DEFINITION as ROUTEBIND

TASK_DEFINITIONS = (ARENA, MAZEHARD, PROSPECT, ROUTEBIND)

__all__ = [
    "ARENA",
    "MAZEHARD",
    "PROSPECT",
    "ROUTEBIND",
    "TASK_DEFINITIONS",
]
