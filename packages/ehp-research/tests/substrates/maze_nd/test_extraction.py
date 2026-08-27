"""Tests for Maze-ND extraction profile (``maze-nd:extraction/raster/v1``).

Covers overlay removal correctness, token classification, the inputs-as-sole-
authority and labels-cross-check contract, and the malformed/unsupported
negative cases (unsupported token, undeclared overlay, wrong extent, missing
field, inputs/labels disagreement).
"""

from __future__ import annotations

import pytest
from ehp_research.substrates.maze_nd.extraction import (
    WALL_TOKEN,
    ExtractionError,
    classify_input_token,
    extract_row,
)
from ehp_research.substrates.maze_nd.extraction import (
    is_passable_input_token as is_passable,
)

from . import _fixtures as fx


def _extract(*rows: str, **kw):
    return extract_row(
        fx.row(fx.grid_from_strings(*rows)), split_file="train.jsonl.gz", row_ordinal=0, **kw
    )


def test_overlay_removal_retains_passability() -> None:
    """Start/goal overlays are removed before identity; their cells stay passable."""
    extracted = _extract("#S#", "#G#")
    # 2x3, passable cells are the S and G cells (columns 1), walls elsewhere.
    assert extracted.height == 2
    assert extracted.width == 3
    # row-major: [c0 wall, c1 passable, c2 wall] x2
    assert extracted.passable == (False, True, False, False, True, False)


def test_inputs_is_sole_passability_authority() -> None:
    """A wall in inputs is impassable even if labels marks it otherwise."""
    # A wall is never passable; overlays retain declared passability under inputs.
    assert is_passable("#") is False
    assert is_passable(" ") is True
    assert is_passable("S") is True
    assert is_passable("G") is True


def test_token_classification_interpretations() -> None:
    assert classify_input_token("#") == "wall"
    assert classify_input_token(" ") == "traversable"
    assert classify_input_token("S") == "start-overlay"
    assert classify_input_token("G") == "goal-overlay"


def test_wall_and_traversable_only_grid() -> None:
    extracted = _extract(" # ", " # ")
    assert extracted.height == 2
    assert extracted.width == 3
    # Row0 ' # ' -> [open, wall, open]; row1 likewise.
    assert extracted.passable == (True, False, True, True, False, True)


def test_source_metadata_carried_not_topology() -> None:
    grid = fx.grid_from_strings("#S#", "#G#")
    extracted = extract_row(
        fx.row(grid, puzzle_index=3, group_index=9, set="test"),
        split_file="test.jsonl.gz",
        row_ordinal=4,
    )
    assert extracted.source_metadata == {"puzzle_index": 3, "group_index": 9, "set": "test"}
    assert extracted.split_file == "test.jsonl.gz"
    assert extracted.row_ordinal == 4


def test_wrong_extent_is_rejected() -> None:
    inputs = fx.grid_from_strings("#S#", "#G", "###")
    with pytest.raises(ExtractionError):
        extract_row(fx.row(inputs), split_file="train.jsonl.gz", row_ordinal=0)


def test_unsupported_source_value_is_rejected() -> None:
    inputs = fx.grid_from_strings("#X#", "#G#")
    with pytest.raises(ExtractionError):
        extract_row(fx.row(inputs), split_file="train.jsonl.gz", row_ordinal=0)


def test_undeclared_overlay_in_labels_is_rejected() -> None:
    """A label token outside the declared set (e.g. an undeclared marker) fails."""
    inputs = fx.grid_from_strings("#S#", "#G#")
    labels = fx.grid_from_strings("#S#", "#G#")
    labels[1][1] = "z"  # undeclared token in labels
    with pytest.raises(ExtractionError):
        extract_row(fx.row(inputs, labels=labels), split_file="train.jsonl.gz", row_ordinal=0)


def test_unsupported_solution_overlay_in_inputs_is_rejected() -> None:
    """Solution overlay 'o' is labels-only; in inputs it is an unknown token."""
    inputs = fx.grid_from_strings("#o#", "#G#")
    with pytest.raises(ExtractionError):
        extract_row(fx.row(inputs), split_file="train.jsonl.gz", row_ordinal=0)


def test_solution_overlay_in_labels_is_accepted_and_passable() -> None:
    inputs = fx.grid_from_strings("# #", "#G#")
    labels = fx.grid_from_strings("#o#", "#G#")
    extracted = extract_row(fx.row(inputs, labels=labels), split_file="train.jsonl.gz", row_ordinal=0)
    # 'o' is passable after overlay removal and agrees with inputs' open cell.
    assert extracted.passable == (False, True, False, False, True, False)


def test_missing_field_is_rejected() -> None:
    bad = {"inputs": fx.grid_from_strings("#S#", "#G#")}
    with pytest.raises(ExtractionError):
        extract_row(bad, split_file="train.jsonl.gz", row_ordinal=0)


def test_inputs_labels_disagreement_is_rejected() -> None:
    inputs = fx.grid_from_strings("# #", "# #")
    labels = fx.grid_from_strings("# #", "# #")
    labels[0][1] = "#"  # passable in inputs, wall in labels -> disagreement
    with pytest.raises(ExtractionError):
        extract_row(fx.row(inputs, labels=labels), split_file="train.jsonl.gz", row_ordinal=0)


def test_malformed_row_not_an_object_is_rejected() -> None:
    with pytest.raises(ExtractionError):
        extract_row(["not", "a", "dict"], split_file="train.jsonl.gz", row_ordinal=0)


def test_non_single_char_token_is_rejected() -> None:
    inputs = [[WALL_TOKEN, "ab"], [fx.OPEN, fx.OPEN]]
    with pytest.raises(ExtractionError):
        extract_row(fx.row(inputs), split_file="train.jsonl.gz", row_ordinal=0)


def test_empty_or_non_list_grid_is_rejected() -> None:
    with pytest.raises(ExtractionError):
        extract_row(fx.row([]), split_file="train.jsonl.gz", row_ordinal=0)
