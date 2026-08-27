"""Tests for Maze-ND normalization policy (``maze-nd:normalization/raster/v1``).

Covers padding normalization (none declared/observed for the pinned revision),
semantic extent, coordinate orientation, orientation preservation, passability
representation, deterministic normalized output, and the "rotation/reflection
stays distinct" acceptance.
"""

from __future__ import annotations

import pytest
from ehp_research.substrates.maze_nd.extraction import extract_row
from ehp_research.substrates.maze_nd.normalization import (
    PADDING_REMOVED,
    NormalizationError,
    normalize,
)

from . import _fixtures as fx


def _normalize(*rows: str) -> tuple[int, int, tuple[bool, ...]]:
    extracted = extract_row(
        fx.row(fx.grid_from_strings(*rows)), split_file="train.jsonl.gz", row_ordinal=0
    )
    return normalize(extracted)


def test_no_padding_declared() -> None:
    assert PADDING_REMOVED is False


def test_normalized_extent_is_source_extent() -> None:
    height, width, _ = _normalize("#S#", "#G#")
    assert (height, width) == (2, 3)


def test_same_source_yields_same_normalized_output() -> None:
    a = _normalize("#S#", "#G#")
    b = _normalize("#S#", "#G#")
    assert a == b


def test_orientation_preserved_row_major() -> None:
    """Passability is row-major, top-to-bottom, left-to-right, unrotated."""
    _, _, passable = _normalize(" # ", "S G")
    # row0: [open, wall, open]; row1: [open, open, open] after overlays removed
    assert passable == (True, False, True, True, True, True)


def test_rotation_kept_distinct() -> None:
    """A rotated mirror of the same shape stays distinct (no symmetry canonicalization)."""
    original = _normalize("#S", "  ")  # 2x2: an L-ish passable set
    rotated = _normalize("  ", "#S")
    # Rotating the grid changes the preserved-orientation raster, so equality
    # must NOT collapse them.
    assert original[:2] == rotated[:2]  # same 2x2 extent
    assert original[2] != rotated[2]  # different passability


def test_reflection_kept_distinct() -> None:
    a = _normalize("#S", " G")
    b = _normalize("S#", "G ")
    assert (a[0], a[1]) == (b[0], b[1])
    assert a[2] != b[2]


def test_border_wall_not_cropped_as_padding() -> None:
    """A meaningful border wall cell is never cropped as padding."""
    # A left-column wall row is semantically meaningful, not padding.
    height, width, passable = _normalize("# ", "# ")
    assert (height, width) == (2, 2)
    # The left wall column is preserved, not cropped: [wall, open] both rows.
    assert passable == (False, True, False, True)


def test_empty_normalized_topology_is_rejected() -> None:
    extracted = extract_row(
        fx.row(fx.grid_from_strings("##", "##")), split_file="train.jsonl.gz", row_ordinal=0
    )
    with pytest.raises(NormalizationError):
        normalize(extracted)
