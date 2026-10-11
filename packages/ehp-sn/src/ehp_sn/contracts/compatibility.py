from __future__ import annotations

from dataclasses import dataclass

from .diagnostics import ContractViolation
from .identity import ContractRef
from .validation import CompatibilityValidator


@dataclass(frozen=True, slots=True, kw_only=True)
class CompatibilityRequirement:
    source: ContractRef
    target: ContractRef
    rule: str


@dataclass(frozen=True, slots=True, kw_only=True)
class CompatibilityResult:
    compatible: bool
    violations: tuple[ContractViolation, ...]


def require_compatible(
    source: object,
    target: object,
    *,
    validator: CompatibilityValidator[tuple[object, object]],
) -> None:
    validator.validate((source, target))
