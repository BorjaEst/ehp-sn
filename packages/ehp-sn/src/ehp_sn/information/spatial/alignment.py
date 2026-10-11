from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ...contracts.diagnostics import ContractViolation
from ...contracts.identity import ContractRef
from .coordinates import SpatialPosition
from .domain import GridDomain

SPATIAL_ALIGNMENT_V1 = ContractRef(name="spatial-alignment", version=1)


@runtime_checkable
class CoordinateTransform(Protocol):
    def apply(self, position: SpatialPosition) -> SpatialPosition: ...


@dataclass(frozen=True, slots=True, kw_only=True)
class SpatialAlignment:
    source: GridDomain
    target: GridDomain
    transform: CoordinateTransform


class SpatialAlignmentValidator:
    def validate(self, value: SpatialAlignment) -> None:
        if len(value.source.shape) != len(value.target.shape):
            raise ContractViolation(
                "aligned domains must share a rank",
                contract=SPATIAL_ALIGNMENT_V1,
                rule="spatial-alignment.rank",
            )
        if value.source.coordinates.axes != value.target.coordinates.axes:
            raise ContractViolation(
                "aligned domains must declare the same axes",
                contract=SPATIAL_ALIGNMENT_V1,
                rule="spatial-alignment.axes",
            )
