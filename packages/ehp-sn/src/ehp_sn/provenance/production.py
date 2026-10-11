from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .configuration import ConfigurationEvidence

if TYPE_CHECKING:
    from ..artifacts.identity import ArtifactRef


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductionEvidence:
    implementation: str
    source_revision: str
    configuration: ConfigurationEvidence
    inputs: Mapping[str, ArtifactRef]
