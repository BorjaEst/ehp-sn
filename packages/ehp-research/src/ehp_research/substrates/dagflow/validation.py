from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import substrates
from ehp_sn.contracts.data.structures.relations import simple_digraph
from ehp_sn.contracts.data.structures.relations.simple_digraph import Artifact
from ehp_sn.substrates import ValidationLevel

from .configuration import Configuration


@dataclass(frozen=True)
class ValidateResult(substrates.ValidateResult): ...


def validate(artifact: Artifact, level: ValidationLevel) -> ValidateResult: ...


__all__ = ["validate", "ValidationLevel", "ValidateResult"]
