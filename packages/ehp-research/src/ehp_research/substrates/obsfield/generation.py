from __future__ import annotations

import numpy as np
from ehp_sn import ObservationField, RasterTopology

from .definition import ObsfieldDefinition
from .settings import ObsfieldSettings


class ObsfieldGenerator:
    def __init__(self, *, settings: ObsfieldSettings) -> None:
        self._settings = settings

    def generate(self, topology: RasterTopology, *, seed: int) -> ObsfieldDefinition:
        domain = topology.domain
        channels = {name: np.zeros(domain.shape, dtype=np.int64) for name in self._settings.channels}
        return ObsfieldDefinition(
            domain=domain,
            observations=ObservationField(domain=domain, channels=channels),
        )
