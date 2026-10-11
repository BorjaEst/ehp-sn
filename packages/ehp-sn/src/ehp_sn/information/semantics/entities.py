from __future__ import annotations

from dataclasses import dataclass

from ...contracts.diagnostics import ContractViolation
from ...contracts.identity import ContractRef

ENTITY_IDENTITY_V1 = ContractRef(name="entity-identity", version=1)


@dataclass(frozen=True, slots=True, kw_only=True)
class EntityIdentity:
    namespace: str
    identifier: str


class EntityIdentityValidator:
    def validate(self, value: EntityIdentity) -> None:
        if not value.namespace:
            raise ContractViolation(
                "an entity identity must declare a namespace",
                contract=ENTITY_IDENTITY_V1,
                rule="entity-identity.namespace.required",
            )
        if not value.identifier:
            raise ContractViolation(
                "an entity identity must declare an identifier",
                contract=ENTITY_IDENTITY_V1,
                rule="entity-identity.identifier.required",
            )
