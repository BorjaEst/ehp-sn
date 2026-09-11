from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import substrates
from ehp_sn.configuration import LoadedConfiguration


@dataclass(frozen=True)
class Configuration(substrates.Configuration): ...


def resolve(document: LoadedConfiguration) -> Configuration: ...


__all__ = ["Configuration", "resolve"]
