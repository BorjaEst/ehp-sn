"""MazeHard task-case record model.

One MazeHard corpus record represents one generated start–goal route problem over
one raster-topology record (``docs/docs/research/tasks/mazehard.md`` § 9.1).

This module owns the canonical task representation: the exact record fields the
task constructs, validates, and exposes. It is the runtime
:class:`MazeHardCase` that the task builder produces, the validator checks, and
the task figure consumes — the same "canonical task representation" at every
boundary (Stage 6C § 7).
"""

from __future__ import annotations

from dataclasses import dataclass

#: Semantic label classes of the path-labelled target (mazehard.md § 8.3).
WALL = "wall"
FREE = "free"
START = "start"
GOAL = "goal"
PATH = "path"


@dataclass(frozen=True, slots=True)
class MazeHardCase:
    """One canonical MazeHard task case.

    All fields are immutable. ``domain`` and ``passable`` are the authoritative
    topology context (public); ``start``/``goal`` are scalar ambient position
    indices; ``reference_path`` is the deterministic canonical optimal route
    $R^*$; ``reference_labels`` is the path-labelled target over the natural
    raster domain; ``optimal_cost`` is $C^*$; ``environment_id`` is the
    corpus-local topology context identity; ``record_id`` is the task-case
    identity. ``split`` records the corpus split this case belongs to.
    """

    record_id: str
    environment_id: str
    domain: dict
    passable: tuple[bool, ...]
    start: int
    goal: int
    reference_path: tuple[int, ...]
    reference_labels: tuple[str, ...]
    optimal_cost: int
    split: str

    @property
    def position_count(self) -> int:
        return len(self.passable)

    def public_lookup(self, position: int) -> dict:
        """Natural-domain public context for one ambient position (start/goal flags)."""
        return {
            "position": position,
            "start": position == self.start,
            "goal": position == self.goal,
            "passable": self.passable[position],
        }
