from __future__ import annotations

from dataclasses import dataclass

from .identity import ContractRef


class ContractViolation(Exception):
    def __init__(
        self,
        message: str,
        *,
        contract: ContractRef,
        rule: str,
        subject: str | None = None,
    ) -> None:
        super().__init__(message)
        self.contract = contract
        self.rule = rule
        self.subject = subject


@dataclass(frozen=True, slots=True, kw_only=True)
class ValidationReport:
    violations: tuple[ContractViolation, ...]

    def is_valid(self) -> bool:
        return not self.violations
