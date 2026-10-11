from __future__ import annotations

from collections.abc import Iterable

from ehp_sn import SampleRecord

from .resource import MazeHardMazeSource
from .settings import MazeHardSettings


class MazeHardDatasetGenerator:
    def __init__(self, *, settings: MazeHardSettings, source: MazeHardMazeSource) -> None:
        self._settings = settings
        self._source = source

    def generate(self, *, seed: int) -> Iterable[SampleRecord]:
        raise NotImplementedError(
            "mazehard dataset construction requires the task's authoritative specification"
        )
