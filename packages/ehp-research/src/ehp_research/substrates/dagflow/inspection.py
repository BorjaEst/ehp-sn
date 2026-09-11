from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import substrates
from ehp_sn.contracts.data.structures.relations import simple_digraph
from ehp_sn.contracts.data.structures.relations.simple_digraph import Artifact

from .configuration import Configuration


@dataclass(frozen=True)
class SummaryResult(substrates.SummaryResult): ...


def summarize(artifact: Artifact) -> SummaryResult: ...


@dataclass(frozen=True)
class InspectResult(substrates.InspectResult): ...


def inspect(artifact: Artifact, record_id: str) -> InspectResult: ...


__all__ = ["summarize", "inspect", "SummaryResult", "InspectResult"]
