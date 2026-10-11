from __future__ import annotations

from ..datasets.indexed import IndexedDataset
from .transformations import InformationTransform


class DatasetAdapter[S, T]:
    def __init__(
        self,
        *,
        source: IndexedDataset[S],
        transform: InformationTransform[S, T],
    ) -> None:
        self._source = source
        self._transform = transform

    def __len__(self) -> int:
        return len(self._source)

    def __getitem__(self, index: int) -> T:
        return self._transform.transform(self._source[index])


class PredictionAdapter[S, T]:
    def __init__(self, *, transform: InformationTransform[S, T]) -> None:
        self._transform = transform

    def adapt(self, prediction: S) -> T:
        return self._transform.transform(prediction)
