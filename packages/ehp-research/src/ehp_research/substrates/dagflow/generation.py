from __future__ import annotations

import random

from ehp_sn import EdgeRecord, NodeRecord, SimpleDigraph

from .settings import DagflowSettings


class DagflowGenerator:
    def __init__(self, *, settings: DagflowSettings) -> None:
        self._settings = settings

    def generate(self, *, seed: int) -> SimpleDigraph:
        generator = random.Random(seed)
        count = self._settings.node_count
        identifiers = [f"n{index}" for index in range(count)]
        terminal = identifiers[-1]
        edges: set[tuple[str, str]] = set()
        for index in range(count - 1):
            edges.add((identifiers[index], terminal))
            for later in range(index + 1, count - 1):
                if generator.random() < self._settings.add_edge_p:
                    edges.add((identifiers[index], identifiers[later]))
        nodes = tuple(NodeRecord(id=identifier, attributes={}) for identifier in identifiers)
        records = tuple(
            EdgeRecord(source=source, target=target, attributes={}) for source, target in sorted(edges)
        )
        return SimpleDigraph(nodes=nodes, edges=records)
