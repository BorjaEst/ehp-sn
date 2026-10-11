from __future__ import annotations

from .definition import MazeHardTaskDefinition


class MazeHardReferencePlanner:
    def solve(self, task: MazeHardTaskDefinition) -> tuple[tuple[float, ...], ...]:
        raise NotImplementedError(
            "mazehard reference planning requires the task's movement and cost semantics"
        )
