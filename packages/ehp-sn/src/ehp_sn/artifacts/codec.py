from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ..contracts.identity import ContractRef
from .manifest import ArtifactManifest


class ArtifactCodec[T](Protocol):
    def category(self) -> str: ...

    def representation(self) -> str: ...

    def contracts(self) -> tuple[ContractRef, ...]: ...

    def write(self, value: T, destination: Path) -> None: ...

    def read(self, source: Path, manifest: ArtifactManifest) -> T: ...
