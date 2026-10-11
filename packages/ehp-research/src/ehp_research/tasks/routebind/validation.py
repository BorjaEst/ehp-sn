from __future__ import annotations

from ehp_sn import ContractRef, ContractViolation

from .definition import RoutebindTaskDefinition
from .settings import RoutebindSettings

ROUTEBIND_V1 = ContractRef(name="routebind", version=1)


class RoutebindSettingsValidator:
    def validate(self, value: RoutebindSettings) -> None:
        if value.route_length < 1:
            raise ContractViolation(
                "route_length must be at least 1",
                contract=ROUTEBIND_V1,
                rule="routebind.parameter.route_length",
                subject="route_length",
            )
        if not value.target_mode:
            raise ContractViolation(
                "routebind must declare a target mode",
                contract=ROUTEBIND_V1,
                rule="routebind.parameter.target_mode",
                subject="target_mode",
            )


class RoutebindCompatibilityValidator:
    def validate(self, value: RoutebindTaskDefinition) -> None:
        nodes = [node.id for node in value.graph.nodes]
        if len(set(nodes)) != len(nodes):
            raise ContractViolation(
                "graph node identifiers must be unique",
                contract=ROUTEBIND_V1,
                rule="routebind.compatibility.nodes",
            )
        sources = list(value.correspondence.source_ids)
        if len(set(sources)) != len(sources):
            raise ContractViolation(
                "the correspondence must be injective over its source domain",
                contract=ROUTEBIND_V1,
                rule="routebind.compatibility.injective",
            )
        if set(sources) != set(nodes):
            raise ContractViolation(
                "the correspondence must cover exactly the graph nodes",
                contract=ROUTEBIND_V1,
                rule="routebind.compatibility.bijection",
            )


class RoutebindDatasetValidator:
    def validate(self, value: object) -> None:
        if not hasattr(value, "__len__"):
            raise ContractViolation(
                "a routebind dataset must be indexable",
                contract=ROUTEBIND_V1,
                rule="routebind.dataset.indexed",
            )
