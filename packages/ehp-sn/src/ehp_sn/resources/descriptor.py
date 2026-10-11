from __future__ import annotations

from dataclasses import dataclass

from ..contracts.identity import ContractRef


@dataclass(frozen=True, slots=True, kw_only=True)
class ResourceDescriptor:
    id: str
    version: str
    kind: str
    location: str
    digest: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class GeneratorResource:
    descriptor: ResourceDescriptor
    interface: ContractRef


@dataclass(frozen=True, slots=True, kw_only=True)
class SnapshotResource:
    descriptor: ResourceDescriptor
    content: tuple[ContractRef, ...]
