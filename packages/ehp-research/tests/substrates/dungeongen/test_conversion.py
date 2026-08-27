"""DungeonGen conversion, normalization, and largest-component tests (Targets 5-7)."""

from __future__ import annotations

import pytest
from ehp_research.substrates.dungeongen.conversion import (
    ConversionError,
    convert_to_passability,
    is_passable_native_cell,
    largest_component,
    normalize_extent,
)

from ._fixtures import BLOCKED, EMPTY, PASSAGE, RESERVED, ROOM, make_fake_candidate


def test_is_passable_native_cell_room_and_passage() -> None:
    """ROOM and PASSAGE are passable; empty/wall/blocked/reserved are not."""
    assert is_passable_native_cell(ROOM)
    assert is_passable_native_cell(PASSAGE)
    assert not is_passable_native_cell(EMPTY)
    assert not is_passable_native_cell(RESERVED)
    assert not is_passable_native_cell(BLOCKED)


def test_convert_to_passability_selects_room_and_passage_only() -> None:
    """Conversion yields exactly the ROOM/PASSAGE cells (doors/stairs/
    exits are passable because their base type is passable)."""
    candidate = make_fake_candidate(
        {
            (0, 0): ROOM,  # passable
            (1, 0): PASSAGE,  # passable (e.g. corridor + door/stair/exit modifier)
            (2, 0): EMPTY,  # non-passable
            (3, 0): RESERVED,  # non-passable
            (4, 0): BLOCKED,  # non-passable
        }
    )
    assert convert_to_passability(candidate) == ((0, 0), (1, 0))


def test_normalize_extent_translates_negative_origin() -> None:
    """A native canvas with negative offsets normalizes to origin (0,0)."""
    # Native cells at negative offsets forming a 2x3 rectangle.
    passable = ((-2, -1), (-1, -1), (0, -1), (-2, 0), (-1, 0), (0, 0))
    height, width, flat = normalize_extent(passable)
    assert (height, width) == (2, 3)
    # Row 0 = native y=-1, Row 1 = native y=0.
    assert flat == (True, True, True, True, True, True)


def test_normalize_extent_offset_invariance() -> None:
    """Acceptance: same geometry at different canvas offsets → same topology."""
    base = ((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1))
    offset = tuple((x + 7, y - 3) for (x, y) in base)
    assert normalize_extent(base) == normalize_extent(offset)


def test_normalize_extent_empty_raises() -> None:
    with pytest.raises(ConversionError):
        normalize_extent(())


def test_largest_component_retains_greatest_cell_count() -> None:
    """The greatest four-connected component is retained."""
    # 3x3 with one 4-cell connected component.
    passable = (
        # row0
        True,
        True,
        True,
        # row1
        False,
        False,
        True,
        # row2
        False,
        False,
        False,
    )
    h, w, flat = largest_component(3, 3, passable)
    # The retained component is the 4-cell one: (0,0),(0,1),(0,2),(1,2).
    states = sum(1 for p in flat if p)
    assert states == 4
    assert (h, w) == (2, 3)


def test_largest_component_tie_break_is_lexicographic() -> None:
    """Acceptance: equal-size components → lexicographic (min row, min col)."""
    # 4x2 grid with two 2-cell vertical components at columns 0 and 3.
    # component at col0: (0,0),(1,0); component at col3: (0,3),(1,3).
    grid = [["."] * 4 for _ in range(2)]
    grid[0][0] = grid[1][0] = "x"  # column 0
    grid[0][3] = grid[1][3] = "x"  # column 3
    flat = tuple(cell == "x" for row in grid for cell in row)
    h, w, retained = largest_component(2, 4, flat)
    # Both components have min (row=0,col); lexicographically smallest col is 0.
    assert (h, w) == (2, 1)
    assert retained == (True, True)
