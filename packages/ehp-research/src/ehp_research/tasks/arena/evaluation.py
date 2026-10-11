from __future__ import annotations

from collections.abc import Sequence

from ehp_sn import EpisodeRecord, EvaluationResult, PredictionRecord


class ArenaEvaluator:
    def evaluate(
        self,
        *,
        predictions: Sequence[PredictionRecord],
        references: Sequence[EpisodeRecord],
    ) -> EvaluationResult:
        raise NotImplementedError(
            "arena evaluation semantics require the task's authoritative specification"
        )
