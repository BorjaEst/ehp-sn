from __future__ import annotations

from dataclasses import dataclass
from typing import *

import ehp_sn.contracts.substrates as contracts
from ehp_sn.contracts.data.structures.relations import simple_digraph

from .configuration import Configuration


@dataclass(frozen=True)
class BuildResult(contracts.BuildResult): ...


def generate(config: Configuration) -> BuildResult: ...


__all__ = ["generate", "BuildResult"]
