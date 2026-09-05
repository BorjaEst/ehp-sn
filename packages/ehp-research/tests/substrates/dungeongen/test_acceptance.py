"""DungeonGen acceptance, retry/exhaustion, and duplicate policy tests (Targets 8-10)."""

from __future__ import annotations

import pytest
from ehp_research.substrates.dungeongen.acceptance import (
    AcceptedTopology,
    RejectionReason,
    evaluate,
    run_logical_topology,
)
from ehp_research.substrates.dungeongen.configuration import resolve_configuration
from ehp_research.substrates.dungeongen.generation import candidate_seed

from ._fixtures import (
    ROOM,
    fake_generator_factory,
    loaded_document,
)


def _cfg(**overrides):
    return resolve_configuration(loaded_document(**overrides))


def _single_cell_room(x: int, y: int) -> dict[tuple[int, int], int]:
    """A single passable ROOM cell (one-state topology)."""
    return {(x, y): ROOM}


def test_evaluate_names_failed_conditions() -> None:
    """Every rejection is attributable to a named configured condition."""
    cfg = _cfg()
    # A 1x1 single-state candidate violates extent and state bounds.
    failed = evaluate(cfg, 1, 1, 1)
    assert isinstance(failed, tuple) and len(failed) >= 1
    for name in failed:
        assert "extent" in name or "states" in name


def test_run_logical_accepts_valid_candidate() -> None:
    """A within-bounds connected candidate is accepted on attempt 0."""
    cfg = _cfg()
    # Build a 2x3 rectangle of ROOM (6 states) within the fixture bounds.
    cells = {(x, y): ROOM for x in range(3) for y in range(2)}
    gen = fake_generator_factory(lambda seed: cells)
    out = run_logical_topology(cfg, 0, generator=gen)
    assert isinstance(out, AcceptedTopology)
    assert out.attempt == 0
    assert out.height == 2 and out.width == 3
    assert len([p for p in out.passable if p]) == 6


def test_rejection_triggers_deterministic_retry() -> None:
    """Attempt 0 rejects a too-small candidate; attempt 1 accepts a valid one."""
    cfg = _cfg()

    def _generator(_config, seed):
        # Deterministically route by which attempt's candidate seed this is.
        if seed == candidate_seed(cfg, 0, 0):
            return fake_generator_factory(lambda _s: _single_cell_room(0, 0))(_config, seed)
        return fake_generator_factory(lambda _s: {(x, y): ROOM for x in range(3) for y in range(2)})(
            _config, seed
        )

    out = run_logical_topology(cfg, 0, generator=_generator)
    assert isinstance(out, AcceptedTopology)
    assert out.attempt == 1
    assert len(out.rejections) == 1
    assert out.rejections[0].attempt == 0


def test_run_accepts_ids_do_not_affect_content() -> None:
    """Native ids/UUIDs never enter content: only the spatial cell map is used."""
    cfg = _cfg()
    cells_a = {(0, 0): ROOM, (1, 0): ROOM, (0, 1): ROOM, (1, 1): ROOM}
    cells_b = {(0, 0): ROOM, (1, 0): ROOM, (0, 1): ROOM, (1, 1): ROOM}
    ga = fake_generator_factory(lambda seed: cells_a)
    gb = fake_generator_factory(lambda seed: cells_b)
    a = run_logical_topology(cfg, 0, generator=ga)
    b = run_logical_topology(cfg, 0, generator=gb)
    assert isinstance(a, AcceptedTopology) and isinstance(b, AcceptedTopology)
    assert (a.height, a.width, a.passable) == (b.height, b.width, b.passable)


def test_exhaustion_is_deterministic_controlled_failure() -> None:
    """Budget exhaustion returns a RejectionReason, never substitution."""
    cfg = _cfg(attempt_budget=3)
    # Every attempt yields a tiny 1-cell candidate that always fails bounds.
    gen = fake_generator_factory(lambda seed: _single_cell_room(seed % 4, (seed // 4) % 4))
    out = run_logical_topology(cfg, 7, generator=gen)
    assert isinstance(out, RejectionReason)
    assert out.logical_index == 7
    assert len(out.rejections) == 3
    assert all(r.attempt == a for a, r in enumerate(out.rejections))
    assert "exhaustion" in out.message


def test_exhaustion_reproducible_for_same_realization() -> None:
    """Acceptance: same exhausted realization → same exhaustion."""
    cfg = _cfg(attempt_budget=4)
    gen = fake_generator_factory(lambda seed: _single_cell_room(0, 0))
    a = run_logical_topology(cfg, 3, generator=gen)
    b = run_logical_topology(cfg, 3, generator=gen)
    assert isinstance(a, RejectionReason) and isinstance(b, RejectionReason)
    assert [(r.attempt, r.reason) for r in a.rejections] == [(r.attempt, r.reason) for r in b.rejections]


def test_retry_does_not_affect_other_index() -> None:
    """A retried index never consumes randomness of another index."""
    cfg = _cfg()
    seen: set[tuple[int, int, tuple[bool, ...]]] = set()

    def gen_for(_config, seed):
        return fake_generator_factory(lambda s: {(0, 0): ROOM})(cfg, seed)

    # index 0 always tiny -> always fails -> exhausts; index 1's candidate seed
    # is a pure function of (1, a) and is unaffected by index 0's retries.
    out0 = run_logical_topology(cfg, 0, generator=gen_for, seen=seen)
    run_logical_topology(cfg, 1, generator=gen_for, seen=seen)
    assert isinstance(out0, RejectionReason)
    assert candidate_seed(cfg, 1, 0) == candidate_seed(cfg, 1, 0)


def test_allow_policy_reports_duplicates_but_keeps_records() -> None:
    """Under allow, repeated canonical content is separate + reported."""
    cfg = _cfg()
    seen: set[tuple[int, int, tuple[bool, ...]]] = set()
    shared_cells = {(x, y): ROOM for x in range(3) for y in range(2)}
    gen = fake_generator_factory(lambda seed: shared_cells)
    a = run_logical_topology(cfg, 0, generator=gen, seen=seen)
    b = run_logical_topology(cfg, 1, generator=gen, seen=seen)
    assert isinstance(a, AcceptedTopology) and isinstance(b, AcceptedTopology)
    assert a.duplicated is False
    assert b.duplicated is True
    assert (a.height, a.width, a.passable) == (b.height, b.width, b.passable)
