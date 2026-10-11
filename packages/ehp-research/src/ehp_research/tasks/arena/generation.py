from __future__ import annotations

from ehp_sn import EpisodeRecord

from .definition import ArenaTaskDefinition
from .settings import ArenaSettings


class ArenaEpisodeGenerator:
    def __init__(self, *, task: ArenaTaskDefinition, settings: ArenaSettings) -> None:
        self._task = task
        self._settings = settings

    def generate(self, *, seed: int) -> EpisodeRecord:
        raise NotImplementedError(
            "arena episode construction requires the task's authoritative specification"
        )
