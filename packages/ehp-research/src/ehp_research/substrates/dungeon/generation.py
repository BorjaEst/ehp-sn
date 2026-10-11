from __future__ import annotations

from .definition import DungeonDefinition
from .resource import DungeonResourceSource
from .settings import DungeonSettings


class DungeonGenerator:
    def __init__(self, *, settings: DungeonSettings, resource: DungeonResourceSource) -> None:
        self._settings = settings
        self._resource = resource

    def generate(self, *, seed: int) -> DungeonDefinition:
        topology = self._resource.generate(seed=seed)
        return DungeonDefinition(
            topology=topology,
            metadata={"generator": self._settings.generator, "seed": seed},
        )
