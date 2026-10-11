from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class FieldDefinition:
    dtype: str
    shape: tuple[int | None, ...]
    role: str


@dataclass(frozen=True, slots=True, kw_only=True)
class DatasetSchema:
    inputs: Mapping[str, FieldDefinition]
    targets: Mapping[str, FieldDefinition]
