"""Maze-ND substrate family container.

Exposes the authoritative ``substrate:maze-nd/v1`` definition object
(``MAZE_ND_DEFINITION``) at the discovery level, and the producer-owned
configuration surface (``resolve_configuration``, ``MazeNDConfiguration``,
``MazeNDConfigurationError``) from ``configuration.py`` with its scientific
owner. This package only re-exports them; it defines no semantics itself.
"""

from __future__ import annotations

from .configuration import (
    MazeNDConfiguration,
    MazeNDConfigurationError,
    resolve_configuration,
)
from .definition import MAZE_ND_DEFINITION

__all__ = [
    "MAZE_ND_DEFINITION",
    "MazeNDConfiguration",
    "MazeNDConfigurationError",
    "resolve_configuration",
]
