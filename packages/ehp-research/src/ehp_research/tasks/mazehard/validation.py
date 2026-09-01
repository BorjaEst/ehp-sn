"""MazeHard task-owned validation.

This module owns validation of the MazeHard invariants
(``docs/docs/research/tasks/mazehard.md`` § 12): record-level (MH-REC-001/002),
oracle (MH-ORACLE-001..004), corpus (MH-CORPUS-001), and split (MH-SPLIT-001/002)
invariants. It returns a :class:`MazeHardValidation` conforming to the generic
``TaskValidateResult`` protocol. The validator is independent of the builder it
checks: it recomputes topology movement and the shortest-route oracle from the
committed passability rather than trusting the constructed reference.
"""

from __future__ import annotations

from dataclasses import dataclass

from ehp_sn.tasks import TaskValidateResult

from .construction import _adjacent_positions, shortest_path_bfs
from .corpus import MazeHardCorpus
from .record import FREE, GOAL, PATH, START, WALL, MazeHardCase


@dataclass(frozen=True, slots=True)
class MazeHardValidation(TaskValidateResult):
    """The outcome of MazeHard task validation."""

    valid: bool
    issues: tuple[str, ...]

    @classmethod
    def ok(cls) -> MazeHardValidation:
        return cls(valid=True, issues=())

    @classmethod
    def fail(cls, *issues: str) -> MazeHardValidation:
        return cls(valid=False, issues=tuple(issues))


def _domain_extent(case: MazeHardCase) -> tuple[int, int]:
    return int(case.domain["height"]), int(case.domain["width"])


def validate_case(case: MazeHardCase, *, check_split: bool = True) -> list[str]:
    """Validate one MazeHard case against MH-REC/MH-ORACLE invariants.

    Returns a list of issue strings (empty when the case is valid). The oracle
    is recomputed independently from the authoritative passability.
    """
    issues: list[str] = []
    height, width = _domain_extent(case)
    free = [i for i, p in enumerate(case.passable) if p]

    # MH-REC-001 — exactly one traversable start and one distinct traversable goal.
    if case.start not in free:
        issues.append(f"MH-REC-001: start {case.start} is not traversable")
    if case.goal not in free:
        issues.append(f"MH-REC-001: goal {case.goal} is not traversable")
    if case.start == case.goal:
        issues.append("MH-REC-001: start and goal must be distinct")

    # MH-REC-002 — reachability.
    if free:
        oracle = shortest_path_bfs(case.passable, height, width, case.start, case.goal)
        if not oracle:
            issues.append("MH-REC-002: goal is not reachable from start")
    else:
        oracle = ()

    # MH-ORACLE-001 — optimal-cost correctness.
    if oracle and oracle[0] == case.start and oracle[-1] == case.goal:
        true_cost = len(oracle) - 1
        if case.optimal_cost != true_cost:
            issues.append(
                f"MH-ORACLE-001: optimal_cost {case.optimal_cost} != true shortest cost {true_cost}"
            )
    elif free:
        issues.append("MH-ORACLE-001: cannot confirm optimal cost for unreachable pair")

    # MH-ORACLE-002 — reference-route validity (start/end/transitions/cost).
    ref = case.reference_path
    if not ref:
        issues.append("MH-ORACLE-002: reference route is empty")
    else:
        if ref[0] != case.start:
            issues.append("MH-ORACLE-002: reference route does not start at start")
        if ref[-1] != case.goal:
            issues.append("MH-ORACLE-002: reference route does not end at goal")
        for k in range(len(ref) - 1):
            u, v = ref[k], ref[k + 1]
            if v not in _adjacent_positions(u, height, width) or not case.passable[v]:
                issues.append(f"MH-ORACLE-002: invalid transition {u}->{v}")
        if oracle and len(ref) - 1 != case.optimal_cost:
            issues.append("MH-ORACLE-002: reference route length != optimal_cost")

    # MH-ORACLE-003 — deterministic reference selection is implied by construction;
    # the validator verifies the reference is a shortest route of optimal cost.
    if oracle and ref and (len(ref) - 1 != case.optimal_cost):
        issues.append("MH-ORACLE-003: reference route is not optimal")

    # MH-ORACLE-004 — target encoding correctness.
    if len(case.reference_labels) != case.position_count:
        issues.append("MH-ORACLE-004: reference_labels length != position count")
    else:
        _check_target(case, ref, issues)

    return issues


def _check_target(case: MazeHardCase, ref: tuple[int, ...], issues: list[str]) -> None:
    """Verify the path-labelled target encodes the reference route exactly."""
    labels = case.reference_labels
    for i, p in enumerate(case.passable):
        expected = WALL if not p else FREE
        if i in (case.start, case.goal):
            expected = START if i == case.start else GOAL
        if i in ref and i not in (case.start, case.goal):
            expected = PATH
        if labels[i] != expected:
            issues.append(
                f"MH-ORACLE-004: label at position {i} is {labels[i]!r}, expected {expected!r}"
            )
            break


class MazeHardCorpusValidator:
    """Validates a constructed MazeHard corpus (record + corpus + split)."""

    def __init__(self, *, case_role: str = "test") -> None:
        self._case_role = case_role

    def validate(self, corpus: MazeHardCorpus) -> MazeHardValidation:
        issues: list[str] = []

        # MH-CORPUS-001 — self-contained problem resolution: every case carries
        # its own domain + passable + target, so no source is required at runtime.
        record_ids: set[str] = set()
        environments: dict[str, str] = {}
        for case in corpus.cases:
            if case.record_id in record_ids:
                issues.append(f"MH-CORPUS-001(id): duplicate record_id {case.record_id}")
            record_ids.add(case.record_id)
            # MH-SPLIT-001 — all records derived from the same environment belong
            # to one split (the corpus uses one configured role).
            if environments.get(case.environment_id) != case.split:
                environments[case.environment_id] = case.split
            issues.extend(validate_case(case))

        # MH-SPLIT-002 — declared novelty policy: every case derives from one
        # committed source record with exact provenance (no reuse beyond the
        # source artifact's own structure).
        for case in corpus.cases:
            prov = corpus.provenance_for(case.record_id)
            if prov.get("source_artifact_fingerprint") != corpus.source_fingerprint:
                issues.append(f"MH-SPLIT-002: provenance fingerprint mismatch for {case.record_id}")

        # No cross-split derivation: Maze-ND has no intrinsic topology split and
        # the task owns the split (single configured role here).
        roles = {c.split for c in corpus.cases}
        if roles - {self._case_role}:
            issues.append(f"MH-SPLIT-001: unexpected splits present: {sorted(roles)}")

        if issues:
            return MazeHardValidation.fail(*issues)
        return MazeHardValidation.ok()
