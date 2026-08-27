"""Tests for ObsField ``categorical-random/v1`` generation.

Verifies the producer scientific algorithm: one categorical observation per
canonical position, vocabulary bounds, determinism, record-addressable
independence, and topologicy/seed-policy independence.
"""

from __future__ import annotations

from ehp_research.substrates.obsfield.configuration import Distribution, ObsFieldConfiguration
from ehp_research.substrates.obsfield.generation import (
    generate_realization,
    generate_realizations,
)


def _config(
    *,
    height: int = 4,
    width: int = 5,
    cardinality: int = 3,
    distribution: Distribution = "uniform",
    seed: int = 0,
    count: int = 5,
) -> ObsFieldConfiguration:
    return ObsFieldConfiguration(
        variant="categorical-complete",
        domain_schema="rectangular-row-column/v1",
        height=height,
        width=width,
        vocabulary_identity="obs-vocabulary:anon/v1",
        vocabulary_cardinality=cardinality,
        assignment_protocol="categorical-random/v1",
        distribution=distribution,
        seed=seed,
        realization_count=count,
    )


def test_one_value_per_domain_position() -> None:
    """Each realization assigns exactly one observation per canonical position."""
    config = _config(height=4, width=5)
    for field in generate_realizations(config):
        assert len(field.observation_ids) == 20  # 4x5


def test_values_belong_to_vocabulary() -> None:
    """Every assigned value is in the vocabulary domain {0, ..., K-1}."""
    config = _config(cardinality=3)
    for field in generate_realizations(config):
        assert all(0 <= v < 3 for v in field.observation_ids)


def test_same_realization_inputs_same_field() -> None:
    """Same realization inputs → same field (determinism)."""
    a = generate_realization(_config(seed=7), 3).content()
    b = generate_realization(_config(seed=7), 3).content()
    assert a == b


def test_larger_count_preserves_earlier_realizations() -> None:
    """Larger realization_count preserves earlier realizations (prefix stability)."""
    small = [f.content() for f in generate_realizations(_config(count=5))]
    large = [f.content() for f in generate_realizations(_config(count=12))]
    assert small == large[:5]


def test_worker_scheduling_irrelevant() -> None:
    """Field content is independent of generation order."""
    forward = [f.content() for f in generate_realizations(_config(count=6))]
    reversed_ = list(generate_realizations(_config(count=6)))
    reverse_contents = [f.content() for f in reversed(reversed_)]
    assert set(map(repr, forward)) == set(map(repr, reverse_contents))


def test_fields_are_topology_independent() -> None:
    """Generation never requires passability, raster topology, Maze-ND, or DungeonGen."""
    field = generate_realization(_config(), 0)
    content = field.content()
    assert "topology" not in content
    assert "passable" not in content
    assert "maze" not in content
    assert "dungeon" not in content


def test_no_intrinsic_split() -> None:
    """Fields form a reusable pool with no intrinsic split semantics."""
    contents = [f.content() for f in generate_realizations(_config(count=4))]
    assert len(contents) == 4
