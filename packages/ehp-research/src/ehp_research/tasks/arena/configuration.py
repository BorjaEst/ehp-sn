from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import tasks
from ehp_sn.configuration import LoadedConfiguration


@dataclass(frozen=True)
class Configuration(tasks.Configuration): ...


def resolve(document: LoadedConfiguration) -> Configuration: ...


__all__ = ["Configuration", "resolve"]
