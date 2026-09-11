from __future__ import annotations

from dataclasses import dataclass
from typing import *

from ehp_sn import substrates

from .configuration import Configuration


@dataclass(frozen=True)
class PlanningDeclaration(substrates.PlanningDeclaration): ...


def create(config: Configuration) -> PlanningDeclaration: ...


__all__ = ["create", "PlanningDeclaration"]
