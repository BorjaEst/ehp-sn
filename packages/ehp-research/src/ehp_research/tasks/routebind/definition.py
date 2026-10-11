from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import EntityCorrespondence, ObservationField, SimpleDigraph


@dataclass(frozen=True, slots=True, kw_only=True)
class RoutebindTaskDefinition:
    graph: SimpleDigraph
    observations: ObservationField
    correspondence: EntityCorrespondence
