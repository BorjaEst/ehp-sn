from __future__ import annotations

from collections.abc import Iterator, Mapping

from ehp_sn import resources
from ehp_sn.contracts.acquisition import maze_examples

from .configuration import Configuration

__all__ = ["ExamplesReader", "MazeExampleFormatError", "decode"]


class MazeExampleFormatError(ValueError):
    """One source record does not conform to the contracted example shape."""


class ExamplesReader:
    """A typed, lazily-decoding reader over verified snapshot members.

    Each call to `records` returns a fresh iterator, so a snapshot can serve
    inspection and multiple consumers without sharing exhausted state.
    """

    def __init__(
        self,
        snapshot: resources.VerifiedSnapshot,
        files: tuple[str, ...],
    ) -> None:
        self._snapshot = snapshot
        self._files = files

    def records(self) -> Iterator[maze_examples.MazeExample]:
        for file_name in self._files:
            yield from self._read_file(file_name)

    def _read_file(self, file_name: str) -> Iterator[maze_examples.MazeExample]:
        with self._snapshot.open(file_name) as stream:
            for row_index, row in enumerate(resources.read_json_lines(stream, name=file_name)):
                yield _decode_record(row, file_name=file_name, row_index=row_index)


def decode(
    *,
    snapshot: resources.VerifiedSnapshot,
    config: Configuration,
) -> maze_examples.MazeExamples:
    """Interpret verified member bytes as authoritative maze examples."""
    return ExamplesReader(snapshot=snapshot, files=config.dataset.files)


def _decode_record(
    row: Mapping[str, object],
    *,
    file_name: str,
    row_index: int,
) -> maze_examples.MazeExample:
    """Interpret one provider record, preserving source identity and membership.

    Malformed content produces a diagnostic naming the member and record; it is
    never silently repaired or skipped.
    """
    try:
        return maze_examples.MazeExample(
            source_id=str(row["id"]),
            inputs=row["input"],
            targets=row["target"],
            membership=str(row["membership"]),
        )
    except KeyError as exc:
        raise MazeExampleFormatError(
            f"{file_name}: record {row_index}: missing required field {exc.args[0]!r}"
        ) from exc
