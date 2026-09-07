from __future__ import annotations

from dataclasses import dataclass
from typing import *

import ehp_sn.contracts.substrates as contracts

from .configuration import Configuration


@dataclass(frozen=True)
class PlanningDeclaration(contracts.PlanningDeclaration): ...


def create(config: Configuration) -> PlanningDeclaration: ...


__all__ = ["create", "PlanningDeclaration"]
