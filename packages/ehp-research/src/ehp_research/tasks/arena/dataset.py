from __future__ import annotations

from collections.abc import Iterator, Sequence

from ehp_sn import EpisodeRecord


class ArenaDataset:
    def __init__(self, *, episodes: Sequence[EpisodeRecord]) -> None:
        self._episodes = tuple(episodes)

    def __len__(self) -> int:
        return len(self._episodes)

    def __getitem__(self, index: int) -> EpisodeRecord:
        return self._episodes[index]

    def __iter__(self) -> Iterator[EpisodeRecord]:
        return iter(self._episodes)
