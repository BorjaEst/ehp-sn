from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class DungeonSettings:
    generator: str
    record_count: int
    duplicate_policy: str
