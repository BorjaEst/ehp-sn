"""Shared synthetic-source helpers for Maze-ND producer tests.

Builds in-memory gzip JSONL source blobs and small grids so the full extraction,
normalization, dedup, lineage, and execution pipeline can be exercised
deterministically and offline. The helpers produce the same row schema
(``inputs`` / ``labels`` / ``puzzle_index`` / ``group_index`` / ``set``) as the
pinned authoritative revision.
"""

from __future__ import annotations

import gzip
import json

from ehp_research.substrates.maze_nd.source import content_fingerprint

WALL = "#"
OPEN = " "
START = "S"
GOAL = "G"
SOLUTION = "o"


def grid_from_strings(*rows: str) -> list[list[str]]:
    """Build a 2-D token grid from rows of single-character source tokens."""
    return [list(row) for row in rows]


def _labels_for_inputs(grid: list[list[str]]) -> list[list[str]]:
    """Derive a labels grid that agrees with ``inputs`` passability.

    Starts/goals stay as overlays; other passable cells stay open; walls stay
    walls. Produces a valid labels cross-check for a valid inputs grid.
    """
    return [[cell if cell in (WALL, START, GOAL) else OPEN for cell in row] for row in grid]


def row(inputs: list[list[str]], **overrides: object) -> dict[str, object]:
    """Build one source problem row with an agreeing labels grid and metadata."""
    return {
        "inputs": inputs,
        "labels": overrides.get("labels", _labels_for_inputs(inputs)),
        "puzzle_index": overrides.get("puzzle_index", 0),
        "group_index": overrides.get("group_index", 0),
        "set": overrides.get("set", "puzzle"),
    }


def split_blob(rows: list[dict[str, object]], *, fingerprint: str | None = None) -> bytes:
    """Serialize rows into a gzip JSONL blob (the exact served form of a split file)."""
    payload = "\n".join(json.dumps(r, separators=(",", ":")) for r in rows).encode("utf-8")
    return gzip.compress(payload)


def blob_fingerprint(train_blob: bytes, test_blob: bytes) -> str:
    """Return the ``sha256:<hex>`` fingerprint over ``train ++ test`` bytes."""
    return content_fingerprint(train_blob, test_blob)


def small_connected_grid() -> list[list[str]]:
    """A tiny fully-connected corridor (2x3) for deterministic tests."""
    return grid_from_strings(
        "#S#",
        "#G#",
    )


def small_disconnected_grid() -> list[list[str]]:
    """A tiny disconnected pair of islands (2x3)."""
    return grid_from_strings(
        "# #",
        "###",
    )
