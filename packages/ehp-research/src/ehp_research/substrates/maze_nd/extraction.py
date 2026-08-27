"""Maze-ND source extraction profile (``maze-nd:extraction/raster/v1``).

This module owns the authoritative Maze-ND extraction interpretation of the
selected external source revision: which source field is the sole topology
authority, how every supported source token and field is classified, how
task-instance overlays are removed while retaining their underlying passability,
and how a source problem row is turned into a validated extracted topology.

Ownership: Maze-ND owns source extraction. It consumes only the parsed JSON
objects of the immutable source revision (see :mod:`.source`) and produces a
validated :class:`ExtractedTopology` that downstream normalization operates on.
It owns no artifact, manifest, resource binding, record identity, or publication
semantics.

The extraction profile classifies every supported source element:

* ``inputs`` (the sole topology authority) — every token is ``#`` (wall),
  `` `` (traversable), ``S`` (start overlay), or ``G`` (goal overlay);
* ``labels`` (verification only) — its tokens add only ``o`` (solution overlay);
  it must equal ``inputs`` passability after overlay removal;
* ``puzzle_index`` / ``group_index`` — source metadata carried in lineage only;
* ``set`` — source split metadata carried in lineage only, never interpreted;
* source split (train/test file membership) — lineage provenance only.

Passability rule: in ``inputs`` a cell is passable iff its token is in
``{" ", "S", "G"}`` and a wall iff ``#``. Any other token makes the row
malformed. Overlay removal happens before topology identity; ``S``/``G``/``o``
cells retain their declared underlying passability. Maze-ND never infers
passability from an overlay without this declared rule.

Malformed rows — wrong extent, unknown token, or an ``inputs``/``labels``
passability disagreement — are rejected with a controlled
:class:`ExtractionError` diagnostic. They are never silently repaired.
"""

from __future__ import annotations

from dataclasses import dataclass

#: The canonical extraction-profile reference.
EXTRACTION_SCHEMA: str = "maze-nd:extraction/raster/v1"

#: Single-character source tokens and their classification.
WALL_TOKEN: str = "#"
TRAVERSABLE_TOKEN: str = " "
START_OVERLAY_TOKEN: str = "S"
GOAL_OVERLAY_TOKEN: str = "G"
SOLUTION_OVERLAY_TOKEN: str = "o"

#: Supported tokens in the authoritative ``inputs`` field.
_SUPPORTED_INPUT_TOKENS: frozenset[str] = frozenset(
    {WALL_TOKEN, TRAVERSABLE_TOKEN, START_OVERLAY_TOKEN, GOAL_OVERLAY_TOKEN}
)
#: Supported tokens in the ``labels`` cross-check field.
_SUPPORTED_LABEL_TOKENS: frozenset[str] = frozenset(
    {WALL_TOKEN, TRAVERSABLE_TOKEN, START_OVERLAY_TOKEN, GOAL_OVERLAY_TOKEN, SOLUTION_OVERLAY_TOKEN}
)

#: Canonical names of source metadata carried in lineage (never topology channels).
SOURCE_METADATA_KEYS: tuple[str, ...] = ("puzzle_index", "group_index", "set")

#: Semantics of every extraction failure.
_WALL = "wall"
_TRAVERSABLE = "traversable"
_START_OVERLAY = "start-overlay"
_GOAL_OVERLAY = "goal-overlay"
_SOLUTION_OVERLAY = "solution-overlay"


def classify_input_token(token: str) -> str:
    """Return the declared interpretation of an ``inputs`` token.

    Raises :class:`ValueError` for an unsupported token. This is the single
    declared interpretation surface for ``inputs`` cells, so no Maze-ND code
    re-derives the meaning of a source symbol ad hoc at runtime.
    """
    if token == WALL_TOKEN:
        return _WALL
    if token == TRAVERSABLE_TOKEN:
        return _TRAVERSABLE
    if token == START_OVERLAY_TOKEN:
        return _START_OVERLAY
    if token == GOAL_OVERLAY_TOKEN:
        return _GOAL_OVERLAY
    raise ValueError(f"unsupported source token {token!r} in inputs")


def is_passable_input_token(token: str) -> bool:
    """Return whether an ``inputs`` token denotes a passable cell.

    A cell is passable iff its token is traversable or a start/goal overlay (an
    overlay declares a passable underlying cell under the extraction profile).
    """
    return token in {TRAVERSABLE_TOKEN, START_OVERLAY_TOKEN, GOAL_OVERLAY_TOKEN}


class ExtractionError(ValueError):
    """A source problem row is malformed or unsupported under the extraction profile.

    Raised by :func:`extract_row` when a row violates a declared extraction
    invariant: unknown token, wrong extent, non-rectangular grid, or an
    ``inputs``/``labels`` passability disagreement. It is a controlled Maze-ND
    semantic failure; the executor translates it as an extraction failure with a
    diagnostic.
    """


@dataclass(frozen=True, slots=True)
class ExtractedTopology:
    """A validated extracted source topology after overlay removal.

    ``height`` / ``width`` are the validated source extent (30 x 30 for the
    pinned revision); ``passable`` is the boolean passability raster in
    canonical row-major order after overlay removal (```` `` ``/``S``/``G``
    passable, ``#`` impassable). ``sources`` identifies the contributing source
    occurrence (split file and row ordinal); the ``source_metadata`` records the
    non-topology source fields for lineage.
    """

    height: int
    width: int
    passable: tuple[bool, ...]
    split_file: str
    row_ordinal: int
    source_metadata: dict[str, object]


def _require_grid(grid: object, field: str) -> list[list[str]]:
    """Validate that ``grid`` is a rectangular ``list[list[str]]`` of single-char tokens."""
    if not isinstance(grid, list) or not grid:
        raise ExtractionError(f"source field {field!r} must be a non-empty list of rows")
    width: int | None = None
    for row_index, row in enumerate(grid):
        if not isinstance(row, list):
            raise ExtractionError(
                f"source field {field!r} row {row_index} must be a list of single-character tokens"
            )
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise ExtractionError(
                f"source field {field!r} is not rectangular: row {row_index} width {len(row)} != {width}"
            )
        for col_index, token in enumerate(row):
            if not isinstance(token, str) or len(token) != 1:
                raise ExtractionError(
                    f"source field {field!r} cell ({row_index},{col_index}) is not a "
                    "single-character token"
                )
    if width is None or width < 1:
        raise ExtractionError(f"source field {field!r} must have at least one column")
    return [[str(tok) for tok in row] for row in grid]


def _is_passable_label_token(token: str) -> bool:
    """Passability under the ``labels`` field: overlays ``S``/``G``/``o`` are passable."""
    return token in {TRAVERSABLE_TOKEN, START_OVERLAY_TOKEN, GOAL_OVERLAY_TOKEN, SOLUTION_OVERLAY_TOKEN}


def _passability(grid: list[list[str]], supported: frozenset[str], field: str) -> list[list[bool]]:
    """Return the passability raster for ``grid``, rejecting unsupported tokens.

    ``field`` selects the passability rule: the authoritative ``inputs`` rule
    treats ```` ``/``S``/``G`` as passable; the ``labels`` cross-check rule also
    treats the solution overlay ``o`` as passable.
    """
    passable_fn = is_passable_input_token if field == "inputs" else _is_passable_label_token
    result: list[list[bool]] = []
    for row_index, row in enumerate(grid):
        out: list[bool] = []
        for col_index, token in enumerate(row):
            if token not in supported:
                raise ExtractionError(
                    f"unsupported source token {token!r} at ({row_index},{col_index}) in field {field!r}"
                )
            out.append(passable_fn(token))
        result.append(out)
    return result


def extract_row(
    row: object,
    *,
    split_file: str,
    row_ordinal: int,
) -> ExtractedTopology:
    """Extract a validated topology from one parsed source problem row.

    ``row`` is a JSON object (a dict) decoded from the immutable source revision.
    ``split_file`` is the source split file the row came from and ``row_ordinal``
    is its 0-based ordinal within that file, together forming the source
    occurrence identity.

    Interprets ``inputs`` as the sole passability authority, removes
    start/goal overlays before identity (retaining passability), and requires
    ``labels`` to reconstruct the same passability after removing its solution
    overlays. Unknown tokens, wrong extent, and disagreement make the row
    malformed and raise :class:`ExtractionError`.

    ``puzzle_index``, ``group_index``, and ``set`` are carried as source metadata
    for lineage; they never become topology channels.
    """
    if not isinstance(row, dict):
        raise ExtractionError(f"source row {row_ordinal} (split {split_file!r}) is not an object")

    for field in ("inputs", "labels"):
        if field not in row:
            raise ExtractionError(
                f"source row {row_ordinal} (split {split_file!r}) is missing required field {field!r}"
            )

    inputs = _require_grid(row["inputs"], "inputs")
    labels = _require_grid(row["labels"], "labels")

    if len(inputs) != len(labels):
        raise ExtractionError(
            f"source row {row_ordinal}: inputs height {len(inputs)} != labels height {len(labels)}"
        )
    if len(inputs[0]) != len(labels[0]):
        raise ExtractionError(
            f"source row {row_ordinal}: inputs width {len(inputs[0])} != labels width {len(labels[0])}"
        )

    height = len(inputs)
    width = len(inputs[0])

    inputs_passable = _passability(inputs, _SUPPORTED_INPUT_TOKENS, "inputs")
    labels_passable = _passability(labels, _SUPPORTED_LABEL_TOKENS, "labels")

    for r in range(height):
        for c in range(width):
            if inputs_passable[r][c] != labels_passable[r][c]:
                raise ExtractionError(
                    f"source row {row_ordinal}: inputs/labels passability disagree at "
                    f"({r},{c}); the row is malformed"
                )

    flat = tuple(cell for r in inputs_passable for cell in r)

    metadata: dict[str, object] = {}
    for key in SOURCE_METADATA_KEYS:
        if key in row:
            metadata[key] = row[key]

    return ExtractedTopology(
        height=height,
        width=width,
        passable=flat,
        split_file=split_file,
        row_ordinal=row_ordinal,
        source_metadata=metadata,
    )


__all__ = [
    "EXTRACTION_SCHEMA",
    "ExtractedTopology",
    "ExtractionError",
    "SOLUTION_OVERLAY_TOKEN",
    "START_OVERLAY_TOKEN",
    "GOAL_OVERLAY_TOKEN",
    "TRAVERSABLE_TOKEN",
    "WALL_TOKEN",
    "classify_input_token",
    "extract_row",
]
