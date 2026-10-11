from __future__ import annotations

from ehp_sn import ObservationField

from .definition import ObsfieldDefinition


class ObsfieldAdapter:
    def to_contract(self, value: ObsfieldDefinition) -> ObservationField:
        return value.observations
