from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ehp_sn import substrates
from ehp_sn.configuration import LoadedConfiguration
from ehp_sn.contracts.data.structures import domains, observations


class ObsFieldConfigurationError(ValueError):
    pass


@dataclass(frozen=True)
class Configuration(substrates.Configuration):
    variant: str
    domain: domains.rectangular_grid.RectangularDomain
    vocabulary: observations.Vocabulary
    assignment_protocol: str
    assignment_parameters: tuple[tuple[str, str], ...]
    seed: int
    realization_count: int


def resolve(document: LoadedConfiguration) -> Configuration:
    """Resolve a declared configuration into semantic values.

    Only declared references are read. Which references this family is able to
    realize is a family declaration, not an assertion made inline.
    """
    values = document.values
    return Configuration(
        variant=_variant(values),
        domain=_domain(values),
        vocabulary=_vocabulary(values),
        assignment_protocol=_protocol(values),
        assignment_parameters=_assignment_parameters(values),
        seed=_seed(values),
        realization_count=_realization_count(values),
    )


def _variant(values: Mapping[str, Any]) -> str:
    """Resolve `substrate.variant` against the variants this family declares."""
    ...


def _domain(values: Mapping[str, Any]) -> domains.rectangular_grid.RectangularDomain:
    """Resolve `domain` through the ambient-domain schemas this family supports."""
    ...


def _vocabulary(values: Mapping[str, Any]) -> observations.Vocabulary:
    """Resolve the declared vocabulary identity and cardinality."""
    ...


def _protocol(values: Mapping[str, Any]) -> str:
    """Resolve `assignment.protocol` against the registered protocols."""
    ...


def _assignment_parameters(values: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    """Read `assignment.parameters` as authored.

    No default is applied here: which parameters exist, which are required, and
    what an omitted parameter means all belong to the resolved protocol.
    """
    ...


def _seed(values: Mapping[str, Any]) -> int:
    """Resolve the base deterministic seed."""
    ...


def _realization_count(values: Mapping[str, Any]) -> int:
    """Resolve how many realizations this artifact requests."""
    ...


__all__ = ["Configuration", "ObsFieldConfigurationError", "resolve"]
