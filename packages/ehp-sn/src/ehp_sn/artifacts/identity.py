from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class ArtifactRef:
    artifact_id: str
    manifest_digest: str
