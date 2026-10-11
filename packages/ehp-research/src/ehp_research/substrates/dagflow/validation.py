from __future__ import annotations

from ehp_sn import ContractRef, ContractViolation, SimpleDigraph

from .settings import DagflowSettings

DAGFLOW_CONSTRUCTIVE_FORWARD = ContractRef(name="dagflow.constructive-forward", version=1)
SUPPORTED_PROTOCOLS = frozenset({"constructive-forward/v1"})


class DagflowSettingsValidator:
    def validate(self, value: DagflowSettings) -> None:
        if value.protocol not in SUPPORTED_PROTOCOLS:
            raise ContractViolation(
                f"unsupported dagflow protocol {value.protocol!r}",
                contract=DAGFLOW_CONSTRUCTIVE_FORWARD,
                rule="dagflow.protocol.supported",
                subject=value.protocol,
            )
        if value.node_count < 1:
            raise ContractViolation(
                "node_count must be at least 1",
                contract=DAGFLOW_CONSTRUCTIVE_FORWARD,
                rule="dagflow.parameter.node_count",
                subject="node_count",
            )
        if not 0.0 <= value.add_edge_p <= 1.0:
            raise ContractViolation(
                "add_edge_p must be within [0, 1]",
                contract=DAGFLOW_CONSTRUCTIVE_FORWARD,
                rule="dagflow.parameter.edge_probability",
                subject="add_edge_p",
            )


class DagflowScientificValidator:
    def validate(self, value: SimpleDigraph) -> None:
        _require_single_terminal_acyclic(value)


def validate_dagflow_generation(graph: SimpleDigraph, *, settings: DagflowSettings) -> None:
    if len(graph.nodes) != settings.node_count:
        raise ContractViolation(
            "graph node count does not match the declared configuration",
            contract=DAGFLOW_CONSTRUCTIVE_FORWARD,
            rule="dagflow.content.node_count",
        )
    _require_single_terminal_acyclic(graph)


def _adjacency(graph: SimpleDigraph) -> dict[str, list[str]]:
    adjacency: dict[str, list[str]] = {node.id: [] for node in graph.nodes}
    for edge in graph.edges:
        adjacency[edge.source].append(edge.target)
    return adjacency


def _has_cycle(adjacency: dict[str, list[str]]) -> bool:
    visiting: set[str] = set()
    settled: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in settled:
            return False
        visiting.add(node)
        for target in adjacency[node]:
            if visit(target):
                return True
        visiting.discard(node)
        settled.add(node)
        return False

    return any(visit(node) for node in adjacency)


def _reaches(adjacency: dict[str, list[str]], start: str, goal: str) -> bool:
    pending = [start]
    seen: set[str] = set()
    while pending:
        node = pending.pop()
        if node == goal:
            return True
        if node in seen:
            continue
        seen.add(node)
        pending.extend(adjacency[node])
    return False


def _require_single_terminal_acyclic(graph: SimpleDigraph) -> None:
    adjacency = _adjacency(graph)
    if _has_cycle(adjacency):
        raise ContractViolation(
            "dagflow graphs must be acyclic",
            contract=DAGFLOW_CONSTRUCTIVE_FORWARD,
            rule="dagflow.content.acyclic",
        )
    terminals = [node for node, targets in adjacency.items() if not targets]
    if len(terminals) != 1:
        raise ContractViolation(
            "dagflow graphs must have exactly one terminal",
            contract=DAGFLOW_CONSTRUCTIVE_FORWARD,
            rule="dagflow.content.single_terminal",
        )
    terminal = terminals[0]
    if not all(_reaches(adjacency, node, terminal) for node in adjacency):
        raise ContractViolation(
            "every node must reach the terminal",
            contract=DAGFLOW_CONSTRUCTIVE_FORWARD,
            rule="dagflow.content.terminal_reachable",
        )
