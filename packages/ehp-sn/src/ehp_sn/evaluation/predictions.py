from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from ..datasets.schema import FieldDefinition


@dataclass(frozen=True, slots=True, kw_only=True)
class PredictionRecord:
    sample_id: str
    outputs: Mapping[str, object]


@dataclass(frozen=True, slots=True, kw_only=True)
class PredictionSchema:
    outputs: Mapping[str, FieldDefinition]
