from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import substrates
from ehp_sn.contracts.data.structures.observations import categorical_field

from .configuration import Configuration
from .planning import random_state_seed, record_id


@dataclass(frozen=True)
class BuildResult(substrates.BuildResult): ...


def generate(config: Configuration) -> BuildResult:
    """Materialize every requested realization of the declared field."""
    records = tuple(
        _realize(config, realization_index) for realization_index in _realization_indexes(config)
    )
    return BuildResult(
        artifact=categorical_field.Artifact(records=records),
        record_count=len(records),
    )


def _realization_indexes(config: Configuration) -> range:
    """Realization indexes requested by this configuration."""
    return range(config.realization_count)


def _realize(config: Configuration, realization_index: int) -> categorical_field.RectangularField:
    """The `obsfield/v1` generation protocol, for one realization index."""
    return categorical_field.RectangularField(
        vocabulary=config.vocabulary,
        observation_id=_assign(config, realization_index),
        record_id=record_id(config, realization_index),
        domain=config.domain,
    )


def _assign(config: Configuration, realization_index: int) -> tuple[int, ...]:
    """One observation per canonical position, in canonical position order."""
    return _draw(
        cardinality=config.vocabulary.cardinality,
        position_count=config.domain.position_count,
        random_state=random_state_seed(config, realization_index),
    )


def _draw(*, cardinality: int, position_count: int, random_state: int) -> tuple[int, ...]:
    """Draw `position_count` categorical labels from a record-local random state."""
    ...


__all__ = ["BuildResult", "generate"]
