from __future__ import annotations

from ..contracts.diagnostics import ContractViolation
from ..contracts.identity import ContractRef
from .descriptor import ResourceDescriptor

EXTERNAL_RESOURCE_V1 = ContractRef(name="external-resource", version=1)


class ResourceDescriptorValidator:
    def validate(self, value: ResourceDescriptor) -> None:
        for field in ("id", "version", "kind", "location"):
            if not getattr(value, field):
                raise ContractViolation(
                    f"resource descriptor must declare {field}",
                    contract=EXTERNAL_RESOURCE_V1,
                    rule=f"external-resource.{field}.required",
                    subject=field,
                )
