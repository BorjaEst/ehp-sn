from __future__ import annotations

from ..contracts.diagnostics import ContractViolation
from .metrics import EVALUATION_RESULTS_V1
from .results import EvaluationResult


class EvaluationResultValidator:
    def validate(self, value: EvaluationResult) -> None:
        if not value.metrics:
            raise ContractViolation(
                "an evaluation result must report at least one metric",
                contract=EVALUATION_RESULTS_V1,
                rule="evaluation-results.metrics.empty",
            )
        names = [metric.metric.name for metric in value.metrics]
        if len(set(names)) != len(names):
            raise ContractViolation(
                "metric names must be unique within a result",
                contract=EVALUATION_RESULTS_V1,
                rule="evaluation-results.metrics.unique",
            )
        for metric in value.metrics:
            if metric.sample_count < 0:
                raise ContractViolation(
                    "metric sample counts must not be negative",
                    contract=EVALUATION_RESULTS_V1,
                    rule="evaluation-results.sample_count.negative",
                    subject=metric.metric.name,
                )
