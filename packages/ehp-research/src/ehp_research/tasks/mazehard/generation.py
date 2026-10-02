from __future__ import annotations

from ehp_sn import substrates
from ehp_sn.contracts.acquisition.maze_examples import MazeExamples

from .configuration import Configuration


def generate(
    config: Configuration,
    *,
    examples: MazeExamples,
) -> substrates.BuildResult[object]: ...


__all__ = ["generate"]
