from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import GridDomain, ObservationField


@dataclass(frozen=True, slots=True, kw_only=True)
class ObsfieldDefinition:
    domain: GridDomain
    observations: ObservationField
