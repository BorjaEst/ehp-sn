from __future__ import annotations

from dataclasses import dataclass

from ..contracts.identity import ContractRef


@dataclass(frozen=True, slots=True, kw_only=True)
class InformationRequirement:
    contract: ContractRef
    fields: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ConsumerRequirements:
    inputs: tuple[InformationRequirement, ...]
    access: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ProducerCapabilities:
    provides: tuple[ContractRef, ...]
    access: tuple[str, ...]
