from __future__ import annotations

from ehp_sn.discovery import ResourceRegistry, SubstrateRegistry, TaskRegistry

from .resources import dungeongen, flaitenberger
from .substrates import dagflow, dungeon, mazend, obsfield
from .tasks import arena, mazehard, prospect, routebind


def register_resources(registry: ResourceRegistry) -> None:
    """Register the resource declarations; never acquire or construct them."""
    registry.register(dungeongen.DEFINITION)
    registry.register(flaitenberger.DEFINITION)


def register_substrates(registry: SubstrateRegistry) -> None:
    registry.register(dagflow.DEFINITION)
    registry.register(dungeon.DEFINITION)
    registry.register(mazend.DEFINITION)
    registry.register(obsfield.DEFINITION)


def register_tasks(registry: TaskRegistry) -> None:
    registry.register(arena.DEFINITION)
    registry.register(mazehard.DEFINITION)
    registry.register(prospect.DEFINITION)
    registry.register(routebind.DEFINITION)


__all__ = ["register_resources", "register_substrates", "register_tasks"]
