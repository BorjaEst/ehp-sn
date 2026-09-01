"""Shared test fixtures for the MazeHard task and 6C conformance suite.

``FakeSource`` is a lightweight, fast, deterministic stand-in for a committed
``raster-topology/v1`` ``SubstrateArtifact`` (only the attributes the task
builder/validator consume). Real committed releases are exercised separately in
producer-substitution tests via ``load_release``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FakeRecord:
    """A minimal logical record exposing the task-consumed surface."""

    record_id: str
    content: dict

    @property
    def descriptors(self) -> tuple:
        return ()


@dataclass
class FakeSource:
    """Minimal stand-in for a committed raster-topology ``SubstrateArtifact``."""

    records: list
    artifact_ref: str = "artifact:fake/source/v1"
    artifact_fingerprint: str = "sha256:fake"


def make_maze_domain(height: int = 5, width: int = 5) -> dict:
    return {
        "schema": "rectangular-row-column/v1",
        "coordinate_system": "row-column",
        "coordinate_structure": "rectangular-lattice",
        "shape": "rectangle",
        "height": height,
        "width": width,
        "position_count": height * width,
    }


def record_with_passable(passable: list[bool], record_id: str = "r1") -> FakeRecord:
    """Build a raster-topology content record with canonical row-major passability.

    The declared domain is inferred so that ``position_count == len(passable)``:
    a ``1 x N`` domain for a single-row corridor, or a square ``K x K`` domain
    when ``len(passable)`` is a perfect square. This keeps the fixture's domain
    and passability consistent (RT-REC-002 coverage).
    """
    n = len(passable)
    root = int(n**0.5)
    if root * root == n:
        height = width = root
    else:
        height, width = 1, n
    content = {
        "domain": make_maze_domain(height=height, width=width),
        "passable": list(passable),
    }
    return FakeRecord(record_id=record_id, content=content)


def corridor_passable(width: int) -> list[bool]:
    """A fully traversable single-row 1 x width corridor (all passable)."""
    return [True] * width


def checkered_passable(height: int, width: int) -> list[bool]:
    """A checkered passable structure (every cell passable)."""
    return [True] * (height * width)
