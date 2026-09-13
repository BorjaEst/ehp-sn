from __future__ import annotations

from dataclasses import dataclass

from . import _core

SCHEMA_REF = "rectangular-grid"
V1 = f"{SCHEMA_REF}/v1"


@dataclass(frozen=True)
class RectangularDomain(_core.Domain):
    """A `rectangular-grid/v1` ambient-domain declaration."""

    height: int
    width: int
    coordinate_system: str = "row-column"
    coordinate_structure: str = "rectangular-lattice"
    shape: str = "rectangle"

    @property
    def position_count(self) -> int:
        return self.height * self.width

    def position_id(self, row: int, column: int) -> int:
        return row * self.width + column

    def coordinates(self, position_id: int) -> tuple[int, int]:
        return divmod(position_id, self.width)


__all__ = ["SCHEMA_REF", "V1", "RectangularDomain"]
