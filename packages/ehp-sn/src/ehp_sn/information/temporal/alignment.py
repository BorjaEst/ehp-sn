from __future__ import annotations

from dataclasses import dataclass

from ...contracts.diagnostics import ContractViolation
from ...contracts.identity import ContractRef

TRANSITION_ALIGNMENT_V1 = ContractRef(name="transition-alignment", version=1)


@dataclass(frozen=True, slots=True, kw_only=True)
class TransitionAlignment:
    observation_offset: int
    action_offset: int
    next_observation_offset: int


class TransitionAlignmentValidator:
    def validate(self, value: TransitionAlignment) -> None:
        if value.observation_offset >= value.next_observation_offset:
            raise ContractViolation(
                "the source observation must precede the next observation",
                contract=TRANSITION_ALIGNMENT_V1,
                rule="transition-alignment.observation.order",
            )
        if value.action_offset >= value.next_observation_offset:
            raise ContractViolation(
                "an action must precede the observation it produces",
                contract=TRANSITION_ALIGNMENT_V1,
                rule="transition-alignment.action.order",
            )
