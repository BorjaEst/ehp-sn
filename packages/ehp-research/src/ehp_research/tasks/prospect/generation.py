from __future__ import annotations

from collections.abc import Iterable

from ehp_sn import SampleRecord

from .definition import ProspectTaskDefinition
from .settings import ProspectSettings


class ProspectDatasetGenerator:
    def __init__(self, *, task: ProspectTaskDefinition, settings: ProspectSettings) -> None:
        self._task = task
        self._settings = settings

    def generate(self, *, seed: int) -> Iterable[SampleRecord]:
        raise NotImplementedError(
            "prospect dataset construction requires the task's authoritative specification"
        )
