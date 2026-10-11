from __future__ import annotations

from dataclasses import dataclass

from ...contracts.diagnostics import ContractViolation
from ...contracts.identity import ContractRef

TIME_AXIS_V1 = ContractRef(name="time-axis", version=1)


@dataclass(frozen=True, slots=True, kw_only=True)
class TimeAxis:
    unit: str
    origin: float
    step: float | None = None


class TimeAxisValidator:
    def validate(self, value: TimeAxis) -> None:
        if not value.unit:
            raise ContractViolation(
                "a time axis must declare a unit",
                contract=TIME_AXIS_V1,
                rule="time-axis.unit.required",
            )
        if value.step is not None and value.step <= 0:
            raise ContractViolation(
                "a discrete time axis must declare a positive step",
                contract=TIME_AXIS_V1,
                rule="time-axis.step.positive",
            )
