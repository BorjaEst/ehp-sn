from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class RoutebindSettings:
    route_length: int
    target_mode: str
