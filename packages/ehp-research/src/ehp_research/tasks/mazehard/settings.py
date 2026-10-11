from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class MazeHardSettings:
    difficulty: str
    sequence_length: int
    encoding: str
