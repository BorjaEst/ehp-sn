from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .identity import ArtifactRef


class InvalidArtifact(Exception):
    def __init__(self, message: str, *, reference: ArtifactRef | None = None) -> None:
        super().__init__(message)
        self.reference = reference


class UnsupportedRepresentation(Exception):
    def __init__(self, message: str, *, representation: str) -> None:
        super().__init__(message)
        self.representation = representation


class ArtifactIntegrityError(Exception):
    def __init__(self, message: str, *, reference: ArtifactRef | None = None) -> None:
        super().__init__(message)
        self.reference = reference
