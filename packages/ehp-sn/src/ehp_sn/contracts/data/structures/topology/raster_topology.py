from __future__ import annotations

from dataclasses import dataclass

SCHEMA_REF = "raster-topology"
V1 = f"{SCHEMA_REF}/v1"


@dataclass(frozen=True)
class Artifact: ...


__all__ = ["Artifact", "SCHEMA_REF", "V1"]
