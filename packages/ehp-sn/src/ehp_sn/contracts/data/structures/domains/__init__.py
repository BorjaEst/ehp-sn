from __future__ import annotations

from . import hexagonal_grid, rectangular_grid
from ._core import ROLE, AmbientDomainError

type Domain = rectangular_grid.RectangularDomain | hexagonal_grid.HexagonalDomain

__all__ = [
    "AmbientDomainError",
    "Domain",
    "ROLE",
    "hexagonal_grid",
    "rectangular_grid",
]
