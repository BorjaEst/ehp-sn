"""MazeHard corpus construction and identity.

This module owns the task-owned corpus build: consuming one committed
``raster-topology/v1`` source artifact, generating one canonical
:class:`MazeHardCase` per selected source record (subject to reachability
admission), and producing a :class:`MazeHardCorpus` exposing the task cases,
their exact source provenance, and deterministic identity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import cast

from ehp_sn.artifacts import SubstrateArtifact
from ehp_sn.tasks import TaskBuildResult

from .construction import MazeHardGenerator, reference_labels, shortest_path_bfs
from .record import MazeHardCase


@dataclass(frozen=True, slots=True)
class MazeHardCorpus(TaskBuildResult):
    """The constructed, self-contained MazeHard corpus (task-build result).

    ``cases`` is the ordered tuple of constructed task cases; ``source_ref`` /
    ``source_fingerprint`` record the exact parent raster-topology artifact;
    ``seed`` is the deterministic generation seed; ``rejected_records`` counts
    source records for which no reachable distinct goal could be generated
    (admission policy). ``provenance`` is the exact ``task_case_id → source
    entity`` mapping required by Stage 6C § 12.
    """

    cases: tuple[MazeHardCase, ...]
    source_ref: str
    source_fingerprint: str
    seed: int
    rejected_records: int = 0
    _provenance: dict[str, dict] = field(default_factory=dict)

    @property
    def records(self) -> tuple[object, ...]:
        return self.cases

    @property
    def resources(self) -> tuple[object, ...]:
        return ()

    @property
    def configuration(self) -> dict:
        return {
            "seed": self.seed,
            "source_ref": self.source_ref,
            "source_fingerprint": self.source_fingerprint,
            "admitted_cases": len(self.cases),
            "rejected_records": self.rejected_records,
        }

    def provenance_for(self, record_id: str) -> dict:
        """Exact source provenance for one task case (Stage 6C § 12)."""
        return self._provenance[record_id]


class MazeHardBuilder:
    """Task-owned builder that materializes a :class:`MazeHardCorpus`.

    ``build`` is deterministic: the same corpus seed, source artifact identity,
    and source records always produce the same task cases and identities
    (mazehard.md § 11; Stage 6C § 26 determinism).
    """

    def __init__(self, *, seed: int, split_policy: str = "environment", case_role: str = "test") -> None:
        self._seed = seed
        #: Split ownership: Maze-ND has no intrinsic topology split, so the task
        #: owns the split (mazehard.md § 10.1). All constructed cases belong to
        #: the configured corpus role until a profile defines otherwise.
        self._split_policy = split_policy
        self._case_role = case_role

    def build(self, source: SubstrateArtifact) -> MazeHardCorpus:
        generator = MazeHardGenerator(self._seed)
        cases: list[MazeHardCase] = []
        provenance: dict[str, dict] = {}

        for index, record in enumerate(source.records):
            content = cast(dict, record.content)
            domain = cast(dict, content["domain"])
            passable = tuple(bool(p) for p in content["passable"])
            height, width = int(domain["height"]), int(domain["width"])
            environment_id = f"{source.artifact_ref}::{record.record_id}"

            start, goal = generator.select_start_goal(passable, index)
            if start < 0:
                continue
            path = shortest_path_bfs(passable, height, width, start, goal)
            if not path:
                # Deterministic admission: an unreachable distinct goal is
                # rejected (reachability is required by MH-REC-002).
                continue

            labels = reference_labels(passable, path, start, goal)
            record_id = self._record_identity(source, record.record_id, index, start, goal, path)
            case = MazeHardCase(
                record_id=record_id,
                environment_id=environment_id,
                domain=domain,
                passable=passable,
                start=start,
                goal=goal,
                reference_path=path,
                reference_labels=labels,
                optimal_cost=len(path) - 1,
                split=self._case_role,
            )
            cases.append(case)
            provenance[record_id] = {
                "source_artifact_ref": source.artifact_ref,
                "source_artifact_fingerprint": source.artifact_fingerprint,
                "source_record_id": record.record_id,
                "source_record_descriptor_digest": getattr(record, "record_id", None),
            }

        rejected = max(0, len(source.records) - len(cases))
        return MazeHardCorpus(
            cases=tuple(cases),
            source_ref=source.artifact_ref,
            source_fingerprint=source.artifact_fingerprint,
            seed=self._seed,
            rejected_records=rejected,
            _provenance=provenance,
        )

    def _record_identity(
        self,
        source: SubstrateArtifact,
        source_record_id: str,
        record_index: int,
        start: int,
        goal: int,
        path: tuple[int, ...],
    ) -> str:
        """Deterministic task-case identity (Stage 6C § 27 identity semantics).

        Identity folds the exact source entity, generation seed, selected
        start/goal, and canonical route. A different source record, target
        parameter, or seed yields a different task identity.
        """
        import hashlib

        blob = "|".join(
            [
                self._seed.__str__(),
                source.artifact_fingerprint,
                source_record_id,
                str(record_index),
                str(start),
                str(goal),
                ",".join(str(p) for p in path),
            ]
        ).encode("utf-8")
        return "sha256:" + hashlib.sha256(blob).hexdigest()
