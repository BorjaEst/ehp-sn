from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class DagflowSettings:
    node_count: int
    add_edge_p: float
    protocol: str


@dataclass(frozen=True, slots=True, kw_only=True)
class DagflowGenerationDefinition:
    protocol: str
    seed: int | None = None
