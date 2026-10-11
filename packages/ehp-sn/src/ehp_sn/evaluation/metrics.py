from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ..contracts.identity import ContractRef

EVALUATION_RESULTS_V1 = ContractRef(name="evaluation-results", version=1)


@dataclass(frozen=True, slots=True, kw_only=True)
class MetricDefinition:
    name: str
    direction: str
    unit: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class MetricResult:
    metric: MetricDefinition
    value: float
    sample_count: int


@runtime_checkable
class MetricEvaluator[T](Protocol):
    def evaluate(self, predictions: Sequence[T], references: Sequence[T]) -> MetricResult: ...
