from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ..contracts.identity import ContractRef


@runtime_checkable
class InformationTransform[S, T](Protocol):
    def transform(self, value: S) -> T: ...


@dataclass(frozen=True, slots=True, kw_only=True)
class TransformDefinition:
    source: ContractRef
    destination: ContractRef
    preserves: tuple[str, ...]
