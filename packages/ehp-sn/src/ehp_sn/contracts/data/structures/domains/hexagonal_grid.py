from __future__ import annotations

from dataclasses import dataclass

from . import _core

SCHEMA_REF = "hexagonal-grid"
V1 = f"{SCHEMA_REF}/v1"


@dataclass(frozen=True)
class HexagonalDomain(_core.Domain):
    """A `hexagonal-grid/v1` ambient-domain declaration."""

    pass


@dataclass(frozen=True)
class Artifact: ...


__all__ = ["Artifact", "SCHEMA_REF", "V1", "HexagonalDomain"]
