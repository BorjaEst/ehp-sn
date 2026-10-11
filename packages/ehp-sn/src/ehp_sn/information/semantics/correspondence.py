from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ...contracts.diagnostics import ContractViolation
from ...contracts.identity import ContractRef

ENTITY_CORRESPONDENCE_V1 = ContractRef(name="entity-correspondence", version=1)


@dataclass(frozen=True, slots=True, kw_only=True)
class EntityCorrespondence:
    source_ids: Sequence[str]
    target_ids: Sequence[str]


class CorrespondenceValidator:
    def validate(self, value: EntityCorrespondence) -> None:
        if len(value.source_ids) != len(value.target_ids):
            raise ContractViolation(
                "a correspondence must pair equal numbers of identities",
                contract=ENTITY_CORRESPONDENCE_V1,
                rule="entity-correspondence.length",
            )
        if len(set(value.source_ids)) != len(value.source_ids):
            raise ContractViolation(
                "source identities must be unique",
                contract=ENTITY_CORRESPONDENCE_V1,
                rule="entity-correspondence.source.unique",
            )
        if len(set(value.target_ids)) != len(value.target_ids):
            raise ContractViolation(
                "target identities must be unique",
                contract=ENTITY_CORRESPONDENCE_V1,
                rule="entity-correspondence.target.unique",
            )
