from __future__ import annotations

from dataclasses import dataclass

from ehp_sn.contracts.data.structures.domains import hexagonal_grid, rectangular_grid

from . import _core

SCHEMA_REF = "categorical-field"
V1 = f"{SCHEMA_REF}/v1"


@dataclass(frozen=True)
class CategoricalField(_core.Observations):
    record_id: str


@dataclass(frozen=True)
class RectangularField(CategoricalField):
    domain: rectangular_grid.RectangularDomain


@dataclass(frozen=True)
class HexagonalField(CategoricalField):
    domain: hexagonal_grid.HexagonalDomain


@dataclass(frozen=True)
class Artifact:
    """Minimal container for committed categorical-field records."""

    records: tuple[CategoricalField, ...] = ()


__all__ = [
    "SCHEMA_REF",
    "V1",
    "Artifact",
    "CategoricalField",
    "RectangularField",
    "HexagonalField",
]
