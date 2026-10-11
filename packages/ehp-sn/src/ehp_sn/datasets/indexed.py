from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..contracts.diagnostics import ContractViolation
from ..contracts.identity import ContractRef

INDEXED_DATASET_V1 = ContractRef(name="indexed-dataset", version=1)


@runtime_checkable
class IndexedDataset[T](Protocol):
    def __len__(self) -> int: ...

    def __getitem__(self, index: int) -> T: ...


class IndexedDatasetValidator:
    def validate(self, value: IndexedDataset[object]) -> None:
        size = len(value)
        if size < 0:
            raise ContractViolation(
                "an indexed dataset must not report a negative length",
                contract=INDEXED_DATASET_V1,
                rule="indexed-dataset.length.negative",
            )
