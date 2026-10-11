from __future__ import annotations

from ..contracts.diagnostics import ContractViolation
from ..contracts.identity import ContractRef
from .bindings import InterfaceBinding
from .requirements import ConsumerRequirements, ProducerCapabilities

INTERFACE_COMPATIBILITY_V1 = ContractRef(name="interface-compatibility", version=1)


class InterfaceCompatibilityValidator:
    def validate(
        self,
        value: tuple[ProducerCapabilities, ConsumerRequirements, InterfaceBinding],
    ) -> None:
        producer, consumer, binding = value
        provided = set(producer.provides)
        for requirement in consumer.inputs:
            if requirement.contract not in provided:
                raise ContractViolation(
                    f"producer does not provide contract {requirement.contract.name!r}",
                    contract=INTERFACE_COMPATIBILITY_V1,
                    rule="interface-compatibility.contract.unmet",
                    subject=requirement.contract.name,
                )
        if producer.access and consumer.access not in producer.access:
            raise ContractViolation(
                f"producer does not support access mode {consumer.access!r}",
                contract=INTERFACE_COMPATIBILITY_V1,
                rule="interface-compatibility.access.unmet",
                subject=consumer.access,
            )
        destinations = {field.destination for field in binding.fields}
        for requirement in consumer.inputs:
            for field in requirement.fields:
                if field not in destinations:
                    raise ContractViolation(
                        f"binding does not supply required field {field!r}",
                        contract=INTERFACE_COMPATIBILITY_V1,
                        rule="interface-compatibility.field.unmet",
                        subject=field,
                    )
