from __future__ import annotations

from ehp_sn import artifacts, planning

from .configuration import Configuration


def create(
    config: Configuration,
    *,
    topology: artifacts.ArtifactRef,
    observation: artifacts.ArtifactRef,
) -> planning.PlanningDeclaration: ...


__all__ = ["create"]
