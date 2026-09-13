from __future__ import annotations

from dataclasses import dataclass

from . import _core

SCHEMA_REF = "hexagonal-grid"
V1 = f"{SCHEMA_REF}/v1"


@dataclass(frozen=True)
class HexagonalDomain(_core.Domain):
    """A `hexagonal-grid/v1` ambient-domain declaration slot.

    The domain-specific payload is intentionally incomplete: the coordinate
    convention, finite shape, shape parameters, and canonical enumeration are
    still to be decided. Establishing the sibling contract now keeps the
    hexagonal alternative visible without committing to those semantics
    prematurely.
    """


__all__ = ["SCHEMA_REF", "V1", "HexagonalDomain"]
