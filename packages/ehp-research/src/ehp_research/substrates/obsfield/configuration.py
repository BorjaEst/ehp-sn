from __future__ import annotations

from dataclasses import dataclass
from typing import *

import ehp_sn.contracts.substrates as contracts
from ehp_sn.configuration import ConfigurationError, LoadedConfiguration


@dataclass(frozen=True)
class Configuration(contracts.Configuration): ...


def resolve(document: LoadedConfiguration) -> Configuration: ...


__all__ = ["Configuration", "resolve"]
