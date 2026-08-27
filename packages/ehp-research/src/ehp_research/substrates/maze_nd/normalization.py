"""Maze-ND normalization policy (``maze-nd:normalization/raster/v1``).

This module owns the Maze-ND normalization step that turns a validated
:class:`~ehp_research.substrates.maze_nd.extraction.ExtractedTopology` into the
authoritative normalized extent and row-major passability raster.

Maze-ND v1 preserves source orientation and does not canonicalize rotations,
reflections, transpositions, or symmetries. Two source topologies related only
by such a transformation remain distinct unless their normalized rasters are
already identical in preserved orientation.

The normalization policy removes *only* padding explicitly declared
non-semantic by the extraction profile. For the pinned revision no padding is
declared or observed, so the semantic extent is exactly the source extent
(30 x 30); meaningful border cells are never cropped as padding.

Ownership: Maze-ND owns normalization meaning. It produces the canonical
row-major passability tuple that the shared ``raster-topology/v1`` constructor
consumes; it does not itself enumerate states, compute components, or define
movement (those are delegated to the shared contract).
"""

from __future__ import annotations

from .extraction import ExtractedTopology

#: The canonical normalization-policy reference.
NORMALIZATION_POLICY: str = "maze-nd:normalization/raster/v1"

#: Fixed schema parameter: orientation is preserved (never canonicalized).
ORIENTATION_PRESERVATION: str = "preserved"

#: No padding is declared or observed for the pinned source revision.
PADDING_REMOVED: bool = False


class NormalizationError(ValueError):
    """A normalized topology violates the declared normalization policy.

    Raised when normalized output would be inconsistent with the extraction
    profile (for example an empty semantic canvas). It is a controlled Maze-ND
    failure; the executor translates it as a normalization failure.
    """


def normalize(extracted: ExtractedTopology) -> tuple[int, int, tuple[bool, ...]]:
    """Return the authoritative normalized ``(height, width, passable)``.

    Overlay removal is already applied by extraction. The policy here:

    * removes declared non-semantic padding (none for the pinned revision, so
      extent stays the source extent);
    * preserves source orientation exactly (row-major, top-to-bottom,
      left-to-right): no rotation/reflection/transposition/symmetry;
    * emits the authoritative row-major boolean passability raster in that
      preserved orientation.

    The same extracted source topology always yields the same normalized extent
    and passability; the operation is deterministic and pure.
    """
    if extracted.height < 1 or extracted.width < 1:
        raise NormalizationError("normalized topology must have a positive extent")
    if len(extracted.passable) != extracted.height * extracted.width:
        raise NormalizationError("normalized passability length does not match the declared extent")
    if not any(extracted.passable):
        raise NormalizationError("normalized topology must contain at least one passable cell")
    return extracted.height, extracted.width, extracted.passable


__all__ = [
    "NORMALIZATION_POLICY",
    "NormalizationError",
    "ORIENTATION_PRESERVATION",
    "PADDING_REMOVED",
    "normalize",
]
