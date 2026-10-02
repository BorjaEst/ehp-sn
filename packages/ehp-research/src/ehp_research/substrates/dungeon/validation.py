from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import substrates
from ehp_sn.contracts.data.structures.topology.raster_topology import Artifact
from ehp_sn.substrates import ValidationLevel


@dataclass(frozen=True)
class ValidateResult(substrates.ValidateResult): ...


def validate(artifact: Artifact, level: ValidationLevel) -> ValidateResult: ...


__all__ = ["validate", "ValidationLevel", "ValidateResult"]
