"""Shared synthetic helpers for DungeonGen producer tests.

Builds in-memory generic configuration documents (matching the real reusable
profile structure) and deterministic fake native candidates so the full
conversion, component-selection, normalization, acceptance, retry, lineage, and
execution pipeline can be exercised deterministically and offline.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from ehp_research.substrates.dungeongen._dependency import DEPENDENCY_REFERENCE
from ehp_research.substrates.dungeongen.generation import NativeCandidate
from ehp_sn.configuration import LoadedConfiguration

#: Default full first generator profile (mirrors config/data/dungeongen/*.toml).
DEFAULT_PARAMS: dict[str, Any] = {
    "archetype": "classic",
    "size": "medium",
    "room_size_bias": 0.0,
    "round_room_chance": 0.15,
    "hall_chance": 0.1,
    "density": 0.5,
    "symmetry": "none",
    "symmetry_break": 0.2,
    "linearity": 0.3,
    "loop_factor": 0.3,
    "passage_width": 1,
    "winding": 0.0,
    "extra_room_connections": 0.2,
    "extra_passage_junctions": 0.15,
    "levels": 1,
    "stair_frequency": 0.1,
    "water_enabled": False,
    "water_threshold": 0.15,
}


def config_document(
    *,
    record_count: int = 8,
    attempt_budget: int = 20,
    seed: int = 0,
    duplicate_policy: str = "allow",
    params: dict[str, Any] | None = None,
    size_policy: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Build a generic DungeonGen configuration document for resolver tests.

    When ``params`` is provided it is used verbatim as the profile (so tests can
    omit a field to assert a completeness failure); otherwise the full default
    first profile is used.
    """
    effective = dict(params) if params is not None else dict(DEFAULT_PARAMS)
    return {
        "substrate": {"variant": "general"},
        "generator": {
            "dependency": DEPENDENCY_REFERENCE,
            "protocol": "dungeongen/generation/v1",
            "profile": "dungeongen/profile/general/v1",
            "params": effective,
        },
        "conversion": {"policy": "dungeongen:conversion/raster/v1"},
        "acceptance": {
            "policy": "dungeongen:acceptance/size-and-connected/v1",
            "require_connected": True,
        },
        "generation": {
            "attempt_budget": attempt_budget,
            "seed": seed,
            "record_count": record_count,
            "role": "topology-candidate",
        },
        "topology": {
            "duplicate_policy": duplicate_policy,
            "size_policy": size_policy
            or {
                "minimum_height": 2,
                "maximum_height": 12,
                "minimum_width": 2,
                "maximum_width": 12,
                "minimum_states": 4,
                "maximum_states": 100,
            },
        },
    }


def loaded_document(**overrides: Any) -> LoadedConfiguration:
    """Resolve a config document into a framework ``LoadedConfiguration``."""
    values = config_document(**overrides)
    return LoadedConfiguration(source=Path("<fixture>"), values=values)


def make_fake_candidate(cells: dict[tuple[int, int], int], *, seed: int = 0) -> NativeCandidate:
    """Build a ``NativeCandidate`` with the given occupancy cell map.

    ``cells`` maps native ``(x, y)`` to a ``CellType`` int value matching the
    frozen upstream enum: ``ROOM=1``, ``PASSAGE=2`` passable; other values
    non-passable.
    """
    return NativeCandidate(dungeon=None, cells=dict(cells), seed=seed)


#: Occupancy CellType ints (mirror frozen upstream 0.1.14).
ROOM = 1
PASSAGE = 2
EMPTY = 0
RESERVED = 5
BLOCKED = 6


def fake_generator_factory(
    seed_to_cells: Callable[[int], dict[tuple[int, int], int]],
) -> Callable:
    """Return a generator callable mapping a candidate seed to deterministic cells.

    Useful to make retry/exhaustion deterministic: the returned callable has the
    same signature as :func:`ehp_research.substrates.dungeongen.generation.generate_native`.
    """

    def _generate(configuration: Any, seed: int) -> NativeCandidate:
        return make_fake_candidate(seed_to_cells(seed), seed=seed)

    return _generate
