from __future__ import annotations

from dataclasses import dataclass

from ...contracts.diagnostics import ContractViolation
from ...contracts.identity import ContractRef
from .coordinates import CoordinateSystem

GRID_DOMAIN_V1 = ContractRef(name="grid-domain", version=1)


@dataclass(frozen=True, slots=True, kw_only=True)
class GridDomain:
    shape: tuple[int, ...]
    coordinates: CoordinateSystem


class SpatialDomainValidator:
    def validate(self, value: GridDomain) -> None:
        if not value.shape:
            raise ContractViolation(
                "a grid domain must declare at least one dimension",
                contract=GRID_DOMAIN_V1,
                rule="grid-domain.shape.empty",
            )
        if any(dimension < 1 for dimension in value.shape):
            raise ContractViolation(
                "grid domain dimensions must be positive",
                contract=GRID_DOMAIN_V1,
                rule="grid-domain.shape.positive",
            )
        if len(value.shape) != len(value.coordinates.axes):
            raise ContractViolation(
                "the number of axes must match the domain rank",
                contract=GRID_DOMAIN_V1,
                rule="grid-domain.coordinates.rank",
            )
