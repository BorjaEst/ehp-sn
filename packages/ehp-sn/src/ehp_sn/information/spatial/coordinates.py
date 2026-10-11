from __future__ import annotations

from dataclasses import dataclass

from ...contracts.diagnostics import ContractViolation
from ...contracts.identity import ContractRef

COORDINATE_SYSTEM_V1 = ContractRef(name="coordinate-system", version=1)
SPATIAL_POSITION_V1 = ContractRef(name="spatial-position", version=1)


@dataclass(frozen=True, slots=True, kw_only=True)
class CoordinateSystem:
    axes: tuple[str, ...]
    units: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class SpatialPosition:
    coordinates: tuple[float, ...]


class CoordinateSystemValidator:
    def validate(self, value: CoordinateSystem) -> None:
        if not value.axes:
            raise ContractViolation(
                "a coordinate system must declare at least one axis",
                contract=COORDINATE_SYSTEM_V1,
                rule="coordinate-system.axes.empty",
            )
        if len(set(value.axes)) != len(value.axes):
            raise ContractViolation(
                "coordinate axes must be unique",
                contract=COORDINATE_SYSTEM_V1,
                rule="coordinate-system.axes.unique",
            )
        if len(value.units) != len(value.axes):
            raise ContractViolation(
                "each axis must declare exactly one unit",
                contract=COORDINATE_SYSTEM_V1,
                rule="coordinate-system.units.length",
            )
