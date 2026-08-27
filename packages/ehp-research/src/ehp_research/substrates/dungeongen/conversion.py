"""DungeonGen native→passability conversion, normalization, and component policy.

This module owns the DungeonGen producer steps that turn a raw native candidate
into the canonical normalized passability raster:

* :func:`convert_to_passability` — the ``dungeongen:conversion/raster/v1``
  policy: which native occupancy cells are passable;
* :func:`normalize_extent` — semantic-extent normalization: removal
  of the non-semantic canvas origin and recomputation of the canonical extent;
* :func:`largest_component` — the ``dungeongen:selection/largest-component/v1``
  policy: which passable component survives before the shared
  topology is constructed.

The conversion reads the generator's faithful native occupancy raster — the
spatial mapping from native cells to occupancy types that the layout generator
populates from rooms, passages, doors, stairs, and exits. It never reads
rendered PNG/SVG and never exposes native unstable room/door object IDs as
public content.

This step remains producer-owned end-to-end: it decides which component
survives *before* the final ``raster-topology/v1`` topology is constructed. The
shared contract later computes component properties of the final raster; it is
never asked to select a component.
"""

from __future__ import annotations

from collections.abc import Sequence

from .generation import NativeCandidate

#: The four-connected movement offsets over passable cells (grid4).
_GRID4_DELTAS: tuple[tuple[int, int], ...] = ((0, 1), (0, -1), (1, 0), (-1, 0))

#: Native occupancy ``CellType`` values treated as passable:
#: ``ROOM`` and ``PASSAGE``. Doors/stairs/exits are modifiers on such cells.
#: ``EMPTY``, ``WALL``, ``DOOR`` (only a type when emitted), ``RESERVED``, and
#: ``BLOCKED`` are non-passable. Values mirror the frozen upstream 0.1.14 enum.
_CELL_ROOM: int = 1
_CELL_PASSAGE: int = 2


class ConversionError(ValueError):
    """A controlled DungeonGen conversion, normalization, or component failure."""


# ---------------------------------------------------------------------------
# Conversion
# ---------------------------------------------------------------------------


def is_passable_native_cell(cell_type: int) -> bool:
    """Whether a native occupancy cell type is passable under the policy."""
    return cell_type in (_CELL_ROOM, _CELL_PASSAGE)


def convert_to_passability(candidate: NativeCandidate) -> tuple[tuple[int, int], ...]:
    """Return the passable native coordinates for a raw native candidate.

    Under ``dungeongen:conversion/raster/v1``, the passability set is exactly
    the native cells the occupancy raster classifies as ``ROOM`` or ``PASSAGE``
    (which includes cells carrying DOOR / STAIRS / EXIT modifiers and every
    passage and room cell). Coordinates retain their native (x, y) form; the
    semantic-extent normalization is applied by :func:`normalize_extent`.
    """
    return tuple(
        (x, y) for (x, y), cell_type in candidate.cells.items() if is_passable_native_cell(cell_type)
    )


# ---------------------------------------------------------------------------
# Semantic extent normalization
# ---------------------------------------------------------------------------


def _tight_bounds(passable: Sequence[tuple[int, int]]) -> tuple[int, int, int, int] | None:
    """Return ``(min_x, min_y, max_x, max_y)`` of the passable coordinates, or None."""
    if not passable:
        return None
    xs = [p[0] for p in passable]
    ys = [p[1] for p in passable]
    return min(xs), min(ys), max(xs), max(ys)


def normalize_extent(passable: Sequence[tuple[int, int]]) -> tuple[int, int, tuple[bool, ...]]:
    """Return the canonical normalized ``(height, width, passable)``.

    The native canvas origin is non-semantic: every cell strictly outside the
    tight bounding box over passable cells is declared generator canvas margin.
    The retained rectangle is translated to origin ``(0, 0)`` and emitted in
    canonical row-major order (``row = y - min_y``, ``column = x - min_x``).

    Equal native geometry at different irrelevant canvas offsets therefore
    yields the same normalized topology because the offset is declared
    non-semantic.
    """
    bounds = _tight_bounds(passable)
    if bounds is None:
        raise ConversionError(
            "raw candidate contains no passable cell; conversion produced an empty semantic topology"
        )
    min_x, min_y, max_x, max_y = bounds
    height = max_y - min_y + 1
    width = max_x - min_x + 1
    grid = [[False] * width for _ in range(height)]
    for x, y in passable:
        grid[y - min_y][x - min_x] = True
    flat: list[bool] = []
    for row in grid:
        flat.extend(row)
    return height, width, tuple(flat)


# ---------------------------------------------------------------------------
# Largest-component selection
# ---------------------------------------------------------------------------


def _components(height: int, width: int, passable: Sequence[bool]) -> list[tuple[tuple[int, int], ...]]:
    """Return the four-connected passable components as coordinate tuples.

    Four-connected (grid4) adjacency over the normalized row/column grid. Each
    component is returned as its cells; components are discovered in canonical
    row-major scan order (by first cell), which keeps the result deterministic.
    """
    flat = list(passable)
    if len(flat) != height * width:
        raise ConversionError(f"component passability length {len(flat)} != extent {height}x{width}")
    visited = [False] * (height * width)
    components: list[tuple[tuple[int, int], ...]] = []
    for start in range(height * width):
        if not flat[start] or visited[start]:
            continue
        cells: list[tuple[int, int]] = []
        stack = [start]
        visited[start] = True
        while stack:
            pos = stack.pop()
            row, col = divmod(pos, width)
            cells.append((row, col))
            for drow, dcol in _GRID4_DELTAS:
                nrow, ncol = row + drow, col + dcol
                if 0 <= nrow < height and 0 <= ncol < width:
                    npos = nrow * width + ncol
                    if flat[npos] and not visited[npos]:
                        visited[npos] = True
                        stack.append(npos)
        components.append(tuple(cells))
    return components


def largest_component(
    height: int, width: int, passable: Sequence[bool]
) -> tuple[int, int, tuple[bool, ...]]:
    """Select the retained largest four-connected component and re-normalize it.

    Under ``dungeongen:selection/largest-component/v1``:

    1. identify all four-connected passable components;
    2. select the component with the greatest cell count;
    3. on a tie, select the component whose lexicographically smallest
       ``(row, column)`` coordinate is smallest;
    4. discard all other components;
    5. re-normalize the retained component extent to a tight bounding box
       (row-min/col-min translated to origin).

    The returned ``(height, width, passable)`` is connected and has exactly one
    component once the shared ``raster-topology/v1`` constructor derives it.
    """
    if height < 1 or width < 1:
        raise ConversionError("component selection requires a positive extent")
    components = _components(height, width, passable)
    if not components:
        raise ConversionError("component selection found no passable component")
    retained = max(
        components,
        key=lambda comp: (len(comp), tuple((-r, -c) for (r, c) in comp[:1])),
    )
    # Re-normalize the retained component (in row/column grid space) to its
    # tight bounding box translated to origin.
    rows = [r for (r, _c) in retained]
    cols = [c for (_r, c) in retained]
    min_row, max_row = min(rows), max(rows)
    min_col, max_col = min(cols), max(cols)
    out_height = max_row - min_row + 1
    out_width = max_col - min_col + 1
    grid = [[False] * out_width for _ in range(out_height)]
    for r, c in retained:
        grid[r - min_row][c - min_col] = True
    flat: list[bool] = []
    for row in grid:
        flat.extend(row)
    return out_height, out_width, tuple(flat)


__all__ = [
    "ConversionError",
    "convert_to_passability",
    "is_passable_native_cell",
    "largest_component",
    "normalize_extent",
]
