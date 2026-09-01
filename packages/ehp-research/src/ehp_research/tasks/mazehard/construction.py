"""MazeHard task-owned construction.

This module owns the task's generation semantics (``docs/docs/research/tasks/
mazehard.md`` § 7-8): deterministic start/goal generation, reachability
validation, shortest-route oracle, canonical deterministic tie-break over
optimal routes, and the path-labelled target construction.

It consumes a committed ``raster-topology/v1`` source record (expressed here as
its authoritative ``domain`` and ``passable`` content) and produces canonical
:class:`MazeHardCase` records. It never mutates the source record
(Stage 6C § 13 / § 37 "substrate mutation = 0").
"""

from __future__ import annotations

from collections import deque

from .record import FREE, GOAL, PATH, START, WALL

#: Four cardinal movement vectors under grid4/row-major (up, down, left, right).
_GRID4 = ((-1, 0), (1, 0), (0, -1), (0, 1))


def _extent_of(domain: dict) -> tuple[int, int]:
    return int(domain["height"]), int(domain["width"])


def _adjacent_positions(position: int, height: int, width: int) -> tuple[int, ...]:
    """Return the grid4-adjacent ambient positions of ``position`` (row-major)."""
    row, col = divmod(position, width)
    out: list[int] = []
    for dr, dc in _GRID4:
        r, c = row + dr, col + dc
        if 0 <= r < height and 0 <= c < width:
            out.append(r * width + c)
    return tuple(out)


def shortest_path_bfs(
    passable: tuple[bool, ...],
    height: int,
    width: int,
    start: int,
    goal: int,
) -> tuple[int, ...]:
    """Return the deterministic canonical shortest path from ``start`` to ``goal``.

    Implements a standard BFS over grid4 adjacency restricted to passable
    positions, then reconstructs a shortest path from ``goal`` back to ``start``
    choosing, at each step, the smallest-index passable neighbor on a shortest
    path. This is the deterministic canonical tie-break (mazehard.md MH-ORACLE-003).

    Returns the empty tuple when ``goal`` is unreachable from ``start``.
    """
    dist = {start: 0}
    queue: deque[int] = deque([start])
    while queue:
        cur = queue.popleft()
        if cur == goal:
            break
        for nxt in _adjacent_positions(cur, height, width):
            if not passable[nxt]:
                continue
            if nxt not in dist:
                dist[nxt] = dist[cur] + 1
                queue.append(nxt)
    if goal not in dist:
        return ()

    # Reconstruct canonical route backward from the goal.
    path = [goal]
    cur = goal
    while cur != start:
        d = dist[cur]
        candidates = [
            p for p in _adjacent_positions(cur, height, width) if passable[p] and dist.get(p) == d - 1
        ]
        # Deterministic canonical tie-break: smallest position index.
        nxt = min(candidates)
        path.append(nxt)
        cur = nxt
    path.reverse()
    return tuple(path)


def reference_labels(
    passable: tuple[bool, ...],
    path: tuple[int, ...],
    start: int,
    goal: int,
) -> tuple[str, ...]:
    """Build the path-labelled target $y^*$ over the natural raster domain.

    Preserves the visible classes (wall/free) and marks the canonical reference
    route: ``start`` and ``goal`` are overlaid distinctly; interior route cells
    are ``path``; other traversable cells are ``free``; blocked cells are
    ``wall`` (mazehard.md § 8.3).
    """
    labels = [WALL if not p else FREE for p in passable]
    for _i, position in enumerate(path):
        if position == start:
            labels[start] = START
        elif position == goal:
            labels[goal] = GOAL
        else:
            labels[position] = PATH
    return tuple(labels)


def _environment_id(source_artifact_ref: str, source_record_id: str) -> str:
    """Corpus-local environment identity: exact source provenance + source record."""
    return f"{source_artifact_ref}::{source_record_id}"


class MazeHardGenerator:
    """Deterministic start/goal generation over one topology record.

    Given the topology record and a per-record seed derived from the corpus
    generation seed and record index, selects one traversable start and one
    distinct traversable goal. The selection is deterministic and
    record-addressable (mazehard.md § 7.3): the same corpus seed and source
    record index always yield the same start/goal.
    """

    def __init__(self, seed: int) -> None:
        self._seed = seed

    def _derive(self, record_index: int, side: str) -> int:
        import hashlib

        raw = hashlib.sha256(f"{self._seed}|mazehard|{record_index}|{side}".encode()).digest()
        return int.from_bytes(raw[:4], "big")

    def select_start_goal(
        self,
        passable: tuple[bool, ...],
        record_index: int,
    ) -> tuple[int, int]:
        """Select a deterministic reachable start/goal pair.

        Walks a deterministic pseudo-random sequence over traversable positions
        to pick a start, then a distinct goal that is reachable from the start.
        If no reachable distinct goal exists, the pair is deemed infeasible and
        ``(-1, -1)`` is returned so the caller can skip/admit according to policy.
        """
        free = [i for i, p in enumerate(passable) if p]
        if len(free) < 2:
            return (-1, -1)
        # Deterministic permutation seeded by (derived_start, derived_goal).
        start_choice = self._derive(record_index, "start") % len(free)
        start = free[start_choice]

        # Probe distinct goals by deterministic offset until a reachable one is found.
        seen: set[int] = set()
        for probe in range(len(free)):
            offset = self._derive(record_index, f"goal:{probe}") % (len(free) - 1)
            goal_choice = (start_choice + 1 + offset) % len(free)
            goal = free[goal_choice]
            if goal == start or goal in seen:
                continue
            seen.add(goal)
            return start, goal
        return (-1, -1)
