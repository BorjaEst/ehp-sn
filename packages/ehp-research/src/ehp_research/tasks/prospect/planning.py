from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import tasks

from .configuration import Configuration


@dataclass(frozen=True)
class PlanningDeclaration(tasks.PlanningDeclaration): ...


def create(
    config: Configuration,
    *,
    topology: tasks.ResolvedSource,
    observation: tasks.ResolvedSource,
    relations: tasks.ResolvedSource,
) -> PlanningDeclaration: ...


__all__ = ["create", "PlanningDeclaration"]
