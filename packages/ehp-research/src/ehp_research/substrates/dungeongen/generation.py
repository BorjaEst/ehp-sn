from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import substrates

from .configuration import Configuration


@dataclass(frozen=True)
class BuildResult(substrates.BuildResult): ...


def generate(config: Configuration) -> BuildResult: ...


__all__ = ["generate", "BuildResult"]
