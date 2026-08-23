"""Maze-ND substrate family container.

Exposes the authoritative ``substrate:maze-nd/v1`` definition object
(``MAZE_ND_DEFINITION``) at the discovery level. The definition itself lives in
``definition.py`` with its scientific owner; this package only re-exports it.
"""

from __future__ import annotations

from .definition import MAZE_ND_DEFINITION

__all__ = ["MAZE_ND_DEFINITION"]
