from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from ...contracts.diagnostics import ContractViolation
from ...contracts.identity import ContractRef

SIMPLE_DIGRAPH_V1 = ContractRef(name="simple-digraph", version=1)


@dataclass(frozen=True, slots=True, kw_only=True)
class NodeRecord:
    id: str
    attributes: Mapping[str, object]


@dataclass(frozen=True, slots=True, kw_only=True)
class EdgeRecord:
    source: str
    target: str
    attributes: Mapping[str, object]


@dataclass(frozen=True, slots=True, kw_only=True)
class SimpleDigraph:
    nodes: Sequence[NodeRecord]
    edges: Sequence[EdgeRecord]


class SimpleDigraphValidator:
    def validate(self, value: SimpleDigraph) -> None:
        identifiers = [node.id for node in value.nodes]
        if len(set(identifiers)) != len(identifiers):
            raise ContractViolation(
                "node identifiers must be unique",
                contract=SIMPLE_DIGRAPH_V1,
                rule="simple-digraph.node.unique",
            )
        known = set(identifiers)
        pairs: list[tuple[str, str]] = []
        for edge in value.edges:
            if edge.source not in known:
                raise ContractViolation(
                    "edge source must reference a declared node",
                    contract=SIMPLE_DIGRAPH_V1,
                    rule="simple-digraph.edge.source",
                    subject=edge.source,
                )
            if edge.target not in known:
                raise ContractViolation(
                    "edge target must reference a declared node",
                    contract=SIMPLE_DIGRAPH_V1,
                    rule="simple-digraph.edge.target",
                    subject=edge.target,
                )
            if edge.source == edge.target:
                raise ContractViolation(
                    "a simple digraph must not contain self-loops",
                    contract=SIMPLE_DIGRAPH_V1,
                    rule="simple-digraph.edge.self_loop",
                    subject=edge.source,
                )
            pairs.append((edge.source, edge.target))
        if len(set(pairs)) != len(pairs):
            raise ContractViolation(
                "edges must be unique",
                contract=SIMPLE_DIGRAPH_V1,
                rule="simple-digraph.edge.unique",
            )
