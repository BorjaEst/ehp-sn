from __future__ import annotations

from dataclasses import dataclass

from ..provenance.production import ProductionEvidence
from .metrics import MetricResult


@dataclass(frozen=True, slots=True, kw_only=True)
class EvaluationResult:
    metrics: tuple[MetricResult, ...]
    evidence: ProductionEvidence
