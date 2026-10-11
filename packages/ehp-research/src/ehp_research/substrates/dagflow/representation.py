from __future__ import annotations

import networkx as nx
from ehp_sn import EdgeRecord, NodeRecord, SimpleDigraph


class DagflowGraphAdapter:
    def to_contract(self, graph: nx.DiGraph) -> SimpleDigraph:
        nodes = tuple(
            NodeRecord(id=str(node), attributes=dict(graph.nodes[node])) for node in graph.nodes
        )
        edges = tuple(
            EdgeRecord(
                source=str(source),
                target=str(target),
                attributes=dict(graph.edges[source, target]),
            )
            for source, target in graph.edges
        )
        return SimpleDigraph(nodes=nodes, edges=edges)

    def from_contract(self, graph: SimpleDigraph) -> nx.DiGraph:
        result = nx.DiGraph()
        for node in graph.nodes:
            result.add_node(node.id, **node.attributes)
        for edge in graph.edges:
            result.add_edge(edge.source, edge.target, **edge.attributes)
        return result
