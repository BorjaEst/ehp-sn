from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from ...contracts.diagnostics import ContractViolation
from ...contracts.identity import ContractRef
from ..spatial.domain import GridDomain

RASTER_TOPOLOGY_V1 = ContractRef(name="raster-topology", version=1)


@dataclass(frozen=True, slots=True, kw_only=True)
class RasterTopology:
    domain: GridDomain
    cells: ArrayLike
    labels: Mapping[int, str]


class RasterTopologyValidator:
    def validate(self, value: RasterTopology) -> None:
        cells = np.asarray(value.cells)
        if tuple(cells.shape) != tuple(value.domain.shape):
            raise ContractViolation(
                "cell array shape must match the declared domain",
                contract=RASTER_TOPOLOGY_V1,
                rule="raster-topology.cells.shape",
            )
        if not value.labels:
            raise ContractViolation(
                "raster topology must declare cell labels",
                contract=RASTER_TOPOLOGY_V1,
                rule="raster-topology.labels.empty",
            )
        unlabelled = set(np.unique(cells).tolist()) - set(value.labels)
        if unlabelled:
            raise ContractViolation(
                "every cell value must be interpreted by a declared label",
                contract=RASTER_TOPOLOGY_V1,
                rule="raster-topology.cells.labelled",
                subject=str(sorted(unlabelled)),
            )
