"""DungeonGen seed derivation and upstream-parameter mapping tests (Targets 3, 4)."""

from __future__ import annotations

import pytest
from ehp_research.substrates.dungeongen.configuration import resolve_configuration
from ehp_research.substrates.dungeongen.generation import (
    GenerationError,
    candidate_seed,
    to_upstream_params,
    verify_dependency_build_ready,
)

from ._fixtures import loaded_document


def _cfg(**overrides):
    return resolve_configuration(loaded_document(**overrides))


def test_candidate_seed_deterministic_for_same_index_attempt() -> None:
    """Same (i, a) → same candidate seed."""
    cfg = _cfg()
    assert candidate_seed(cfg, 5, 0) == candidate_seed(cfg, 5, 0)
    assert candidate_seed(cfg, 0, 3) == candidate_seed(cfg, 0, 3)


def test_candidate_seed_distinct_across_index_and_attempt() -> None:
    """Retry of i must not reuse/collide with i+1's seed stream."""
    cfg = _cfg()
    seeds = {candidate_seed(cfg, i, a) for i in range(5) for a in range(3)}
    assert len(seeds) == 15  # all distinct


def test_candidate_seed_independent_of_base_seed_change() -> None:
    cfg_a = _cfg(seed=0)
    cfg_b = _cfg(seed=1)
    assert candidate_seed(cfg_a, 2, 0) != candidate_seed(cfg_b, 2, 0)


def test_candidate_seed_in_bounded_nonnegative_range() -> None:
    cfg = _cfg()
    for i in range(50):
        for a in range(3):
            s = candidate_seed(cfg, i, a)
            assert isinstance(s, int)
            assert 0 <= s < (1 << 31)


def test_candidate_seed_validates_nonnegative_arguments() -> None:
    cfg = _cfg()
    with pytest.raises(GenerationError):
        candidate_seed(cfg, -1, 0)
    with pytest.raises(GenerationError):
        candidate_seed(cfg, 0, -1)


def test_to_upstream_params_is_complete() -> None:
    """The resolved profile maps to a complete explicit GenerationParams."""
    cfg = _cfg()
    params = to_upstream_params(cfg.profile)
    # Every upstream field is explicitly set from the profile.
    assert params.passage_width == cfg.profile.passage_width
    assert params.density == cfg.profile.density
    assert params.water_enabled is cfg.profile.water_enabled
    assert params.archetype.name == cfg.profile.archetype.upper()
    assert params.size.name == cfg.profile.size.upper()
    assert params.symmetry.name == cfg.profile.symmetry.upper()


def test_to_upstream_params_room_count_override() -> None:
    """An explicit room_count is passed to upstream and wins over size.

    The upstream ``get_room_count_range`` returns ``room_count`` when set and
    otherwise derives from ``size``; EHP passes ``None`` for the derive-from-size
    state so room-count derivation stays upstream-owned (Correction 3).
    """
    cfg = _cfg(params={"room_count": [6, 10]})
    params = to_upstream_params(cfg.profile)
    assert params.room_count == (6, 10)

    by_size = _cfg(params={"size": "large"})
    size_params = to_upstream_params(by_size.profile)
    assert size_params.room_count is None


def test_verify_dependency_build_ready_passes_for_frozen_version() -> None:
    """The installed dungeongen==0.1.14 is build-ready."""
    verify_dependency_build_ready()
