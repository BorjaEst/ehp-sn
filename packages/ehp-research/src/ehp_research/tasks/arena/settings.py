from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class ArenaSettings:
    horizon: int
    observation_mode: str
    action_mode: str
