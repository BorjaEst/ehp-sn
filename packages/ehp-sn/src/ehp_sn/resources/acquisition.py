from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Protocol, runtime_checkable

from .descriptor import ResourceDescriptor


@runtime_checkable
class ResourceProvider(Protocol):
    def acquire(self, resource: ResourceDescriptor, destination: Path) -> Path: ...


class ResourceAcquirer:
    def __init__(self, *, destination: Path | None = None) -> None:
        self._destination = destination

    def acquire(self, resource: ResourceDescriptor, *, provider: ResourceProvider) -> Path:
        destination = self._destination
        if destination is None:
            destination = Path(tempfile.mkdtemp(prefix="ehp-resource-"))
        destination.mkdir(parents=True, exist_ok=True)
        return provider.acquire(resource, destination)
