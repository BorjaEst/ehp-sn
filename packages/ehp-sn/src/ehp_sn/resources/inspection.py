from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

from ..contracts.identity import ContractRef
from .descriptor import ResourceDescriptor


@runtime_checkable
class ResourceInspector(Protocol):
    def inspect(self, path: Path) -> ResourceDescriptor: ...


@dataclass(frozen=True, slots=True, kw_only=True)
class ResourceInspection:
    descriptor: ResourceDescriptor
    content: tuple[ContractRef, ...]
