from __future__ import annotations

from collections.abc import Sequence

from ehp_sn import EvaluationResult, PredictionRecord, SampleRecord


class ProspectEvaluator:
    def evaluate(
        self,
        *,
        predictions: Sequence[PredictionRecord],
        references: Sequence[SampleRecord],
    ) -> EvaluationResult:
        raise NotImplementedError(
            "prospect evaluation semantics require the task's authoritative specification"
        )
