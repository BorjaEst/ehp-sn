from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ...contracts.diagnostics import ContractViolation
from ...contracts.identity import ContractRef

TOPOLOGY_CONNECTIVITY_V1 = ContractRef(name="topology-connectivity", version=1)


@dataclass(frozen=True, slots=True, kw_only=True)
class TopologyConnectivity:
    components: Sequence[Sequence[str]]


class ConnectivityValidator:
    def validate(self, value: TopologyConnectivity) -> None:
        seen: set[str] = set()
        for component in value.components:
            if not component:
                raise ContractViolation(
                    "components must not be empty",
                    contract=TOPOLOGY_CONNECTIVITY_V1,
                    rule="connectivity.component.empty",
                )
            for identifier in component:
                if identifier in seen:
                    raise ContractViolation(
                        "components must be disjoint",
                        contract=TOPOLOGY_CONNECTIVITY_V1,
                        rule="connectivity.component.disjoint",
                        subject=identifier,
                    )
                seen.add(identifier)
