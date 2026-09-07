from __future__ import annotations

from dataclasses import dataclass
from typing import *

import ehp_sn.contracts.substrates as contracts
from ehp_sn.contracts.data.structures.relations import simple_digraph
from ehp_sn.contracts.data.structures.relations.simple_digraph import Artifact

from .configuration import Configuration


@dataclass(frozen=True)
class ValidationLevel(contracts.ValidationLevel): ...


@dataclass(frozen=True)
class ValidateResult(contracts.ValidateResult): ...


def validate(artifact: Artifact, level: ValidationLevel) -> ValidateResult: ...


__all__ = ["validate", "ValidationLevel", "ValidateResult"]
