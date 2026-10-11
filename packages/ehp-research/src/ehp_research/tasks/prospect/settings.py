from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class ProspectSettings:
    context_length: int
    prediction_horizon: int
    memory_mode: str
