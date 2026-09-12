from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import artifacts
from ehp_sn.contracts import core

SCHEMA_REF = "execution-state"
V1 = f"{SCHEMA_REF}/v1"


@dataclass(frozen=True)
class Artifact: ...


__all__ = ["Artifact", "SCHEMA_REF", "V1"]
