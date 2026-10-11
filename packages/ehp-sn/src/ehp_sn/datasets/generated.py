from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ..contracts.diagnostics import ContractViolation
from ..contracts.identity import ContractRef

GENERATED_DATASET_V1 = ContractRef(name="generated-dataset", version=1)


@runtime_checkable
class GeneratedDataset[T](Protocol):
    def generate(self, *, seed: int | None = None) -> Iterator[T]: ...


@dataclass(frozen=True, slots=True, kw_only=True)
class GenerationDefinition:
    deterministic: bool
    finite: bool
    configurable: bool


class GeneratedDatasetValidator:
    def validate(self, value: GeneratedDataset[object]) -> None:
        for _ in value.generate(seed=0):
            return
        raise ContractViolation(
            "a generated dataset must produce at least one sample",
            contract=GENERATED_DATASET_V1,
            rule="generated-dataset.empty",
        )
