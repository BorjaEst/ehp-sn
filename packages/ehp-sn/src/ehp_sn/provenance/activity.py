from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..artifacts.identity import ArtifactRef


@dataclass(frozen=True, slots=True, kw_only=True)
class ActivityRecord:
    id: str
    operation: str
    inputs: tuple[ArtifactRef, ...]
    outputs: tuple[ArtifactRef, ...]
