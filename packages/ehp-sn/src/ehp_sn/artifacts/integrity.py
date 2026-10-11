from __future__ import annotations

import hashlib
from pathlib import Path

from .errors import ArtifactIntegrityError


class ArtifactIntegrity:
    def digest(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def verify(self, path: Path, expected: str) -> None:
        if self.digest(path) != expected:
            raise ArtifactIntegrityError(f"digest mismatch for {path.name}")
