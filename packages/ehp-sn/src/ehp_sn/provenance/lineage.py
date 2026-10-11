from __future__ import annotations

from dataclasses import dataclass

from .activity import ActivityRecord


@dataclass(frozen=True, slots=True, kw_only=True)
class ArtifactLineage:
    activities: tuple[ActivityRecord, ...]
