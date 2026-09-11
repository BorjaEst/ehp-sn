from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import tasks
from ehp_sn.contracts.data.datasets.sequences import sequence_dataset
from ehp_sn.contracts.data.datasets.sequences.sequence_dataset import Artifact

from .configuration import Configuration


@dataclass(frozen=True)
class SummaryResult(tasks.SummaryResult): ...


def summarize(artifact: Artifact) -> SummaryResult: ...


@dataclass(frozen=True)
class InspectResult(tasks.InspectResult): ...


def inspect(artifact: Artifact, record_id: str) -> InspectResult: ...


__all__ = ["summarize", "inspect", "SummaryResult", "InspectResult"]
