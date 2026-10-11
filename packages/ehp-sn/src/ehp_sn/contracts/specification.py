from __future__ import annotations

from dataclasses import dataclass

from .identity import ContractRef


@dataclass(frozen=True, slots=True, kw_only=True)
class ContractDefinition:
    ref: ContractRef
    description: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ContractRequirement:
    contract: ContractRef
    required: bool = True
