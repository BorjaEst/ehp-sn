import abc

from ehp_sn import core, substrates, tasks


class BaseRegistry(abc.ABC):
    @abc.abstractmethod
    def register(self, definition: core.Definition) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, name: str) -> core.Definition:
        raise NotImplementedError


class SubstrateRegistry:
    def __init__(self) -> None:
        self._registry: dict[str, substrates.Definition] = {}

    def register(self, definition: substrates.Definition) -> None:
        self._registry[definition.ref.name] = definition

    def get(self, name: str) -> substrates.Definition:
        return self._registry[name]


class TaskRegistry:
    def __init__(self) -> None:
        self._registry: dict[str, tasks.Definition] = {}

    def register(self, definition: tasks.Definition) -> None:
        self._registry[definition.ref.name] = definition

    def get(self, name: str) -> tasks.Definition:
        return self._registry[name]


__all__ = [
    "SubstrateRegistry",
    "TaskRegistry",
]
