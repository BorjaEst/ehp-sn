from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import tasks

from .configuration import Configuration


@dataclass(frozen=True)
class BuildResult(tasks.BuildResult): ...


def generate(
    config: Configuration,
    *,
    topology: tasks.ResolvedSource,
) -> BuildResult: ...


__all__ = ["generate", "BuildResult"]
