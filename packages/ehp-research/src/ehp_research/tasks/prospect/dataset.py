from __future__ import annotations

from collections.abc import Iterator, Sequence

from ehp_sn import SampleRecord


class ProspectDataset:
    def __init__(self, *, samples: Sequence[SampleRecord]) -> None:
        self._samples = tuple(samples)

    def __len__(self) -> int:
        return len(self._samples)

    def __getitem__(self, index: int) -> SampleRecord:
        return self._samples[index]

    def __iter__(self) -> Iterator[SampleRecord]:
        return iter(self._samples)
