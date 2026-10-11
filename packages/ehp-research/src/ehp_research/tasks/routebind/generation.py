from __future__ import annotations

from collections.abc import Iterable

from ehp_sn import SampleRecord

from .definition import RoutebindTaskDefinition
from .settings import RoutebindSettings


class RoutebindDatasetGenerator:
    def __init__(self, *, task: RoutebindTaskDefinition, settings: RoutebindSettings) -> None:
        self._task = task
        self._settings = settings

    def generate(self, *, seed: int) -> Iterable[SampleRecord]:
        raise NotImplementedError(
            "routebind dataset construction requires the task's authoritative specification"
        )
