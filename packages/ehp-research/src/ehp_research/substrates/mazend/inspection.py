from __future__ import annotations

from dataclasses import dataclass
from typing import *

import ehp_sn.contracts.substrates as contracts
from ehp_sn.contracts.topology import raster_topology
from ehp_sn.contracts.topology.raster_topology import Artifact

from .configuration import Configuration


@dataclass(frozen=True)
class SummaryResult(contracts.SummaryResult): ...


def summarize(artifact: Artifact) -> SummaryResult: ...


@dataclass(frozen=True)
class InspectResult(contracts.InspectResult): ...


def inspect(artifact: Artifact, record_id: str) -> InspectResult: ...


__all__ = ["summarize", "inspect", "SummaryResult", "InspectResult"]
