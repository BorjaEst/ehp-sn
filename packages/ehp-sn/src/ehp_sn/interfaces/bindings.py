from __future__ import annotations

from dataclasses import dataclass

from ..contracts.diagnostics import ContractViolation
from .requirements import ConsumerRequirements, ProducerCapabilities


@dataclass(frozen=True, slots=True, kw_only=True)
class FieldBinding:
    source: str
    destination: str


@dataclass(frozen=True, slots=True, kw_only=True)
class InterfaceBinding:
    fields: tuple[FieldBinding, ...]
    transformation: str | None = None


class InterfaceBinder:
    def bind(
        self,
        *,
        producer: ProducerCapabilities,
        consumer: ConsumerRequirements,
    ) -> InterfaceBinding:
        provided = set(producer.provides)
        fields: list[FieldBinding] = []
        for requirement in consumer.inputs:
            if requirement.contract not in provided:
                raise ContractViolation(
                    f"producer does not provide contract {requirement.contract.name!r}",
                    contract=requirement.contract,
                    rule="interface.requirement.unmet",
                )
            fields.extend(FieldBinding(source=field, destination=field) for field in requirement.fields)
        return InterfaceBinding(fields=tuple(fields), transformation=None)
