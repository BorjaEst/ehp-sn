from __future__ import annotations

from ehp_sn import planning
from ehp_sn.contracts.acquisition.maze_examples import MazeExamples

from .configuration import Configuration


def create(
    config: Configuration,
    *,
    examples: MazeExamples,
) -> planning.PlanningDeclaration: ...


__all__ = ["create"]
