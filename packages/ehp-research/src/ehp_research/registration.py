from __future__ import annotations

from ehp_sn.discovery import SubstrateRegistry, TaskRegistry

from .substrates import dagflow, dungeongen, mazend, obsfield
from .tasks import arena, mazehard, prospect, routebind


def register_substrates(registry: SubstrateRegistry) -> None:
    registry.register(dagflow.DEFINITION)
    registry.register(dungeongen.DEFINITION)
    registry.register(mazend.DEFINITION)
    registry.register(obsfield.DEFINITION)


def register_tasks(registry: TaskRegistry) -> None:
    registry.register(arena.DEFINITION)
    registry.register(mazehard.DEFINITION)
    registry.register(prospect.DEFINITION)
    registry.register(routebind.DEFINITION)


__all__ = ["register_substrates", "register_tasks"]
