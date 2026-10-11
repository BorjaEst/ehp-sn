from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class SampleRecord:
    inputs: Mapping[str, object]
    targets: Mapping[str, object]
    metadata: Mapping[str, object]


@dataclass(frozen=True, slots=True, kw_only=True)
class TransitionRecord:
    observation: object
    action: object
    next_observation: object
    metadata: Mapping[str, object]


@dataclass(frozen=True, slots=True, kw_only=True)
class EpisodeRecord:
    observations: Sequence[object]
    actions: Sequence[object]
    metadata: Mapping[str, object]
