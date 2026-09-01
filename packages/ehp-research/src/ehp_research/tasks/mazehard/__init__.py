"""MazeHard task family.

MazeHard (``task:maze-hard/v1``) is a fully observed static shortest-route
prediction task over a raster maze (``docs/docs/research/tasks/mazehard.md``).
It consumes one compatible ``raster-topology/v1`` source record, generates a
deterministic reachable start–goal query, computes the canonical shortest-route
truth, and materializes self-contained task cases.
"""

from __future__ import annotations

from .corpus import MazeHardBuilder, MazeHardCorpus
from .definition import MAZEHARD_DEFINITION, MazeHardDefinition
from .record import MazeHardCase
from .validation import MazeHardCorpusValidator, MazeHardValidation, validate_case

__all__ = [
    "MAZEHARD_DEFINITION",
    "MazeHardBuilder",
    "MazeHardCase",
    "MazeHardCorpus",
    "MazeHardCorpusValidator",
    "MazeHardDefinition",
    "MazeHardValidation",
    "validate_case",
]
