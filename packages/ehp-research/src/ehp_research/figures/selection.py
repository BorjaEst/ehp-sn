"""Research-owned deterministic cell selection for the HPC place summary (Phase 3).

This module defines the HPC-owned selection semantics
:class:`TopSpatialInformationCells` and its deterministic resolver.

The selection is research-owned (``ehp_research``), not framework-owned
(``P3-T4``). The framework provides only the generic ``ResolvedFigureSelection``
envelope and reproducibility requirements; the concrete scientific meaning —
candidate population, eligibility, ranking metric, sort direction, cardinality,
tie-breaking, and non-finite handling — is defined here.

## Declared semantics

```text
candidate population:  valid cells in the authoritative HPC analysis
eligibility:           cell.spatial_information is finite (see HpcAnalysis.valid_cells)
ranking metric:        spatial_information
order:                 descending (highest first)
tie-break:             cell_id ascending
non-finite metric:     excluded
required count:        count (exactly, or a controlled selection failure)
duplicate cell identity:
                       authoritative source must not contain duplicate cell_ids;
                       a violation is a source-contract validation failure
insufficient valid cells:
                       controlled selection failure (do not silently reduce count)
```

``count=8`` means exactly 8 cells, not "up to 8". If future behavior needs an
"up to N" semantic, it is a separate, explicitly defined selection policy, not a
relaxation of this one.

Determinism: resolution operates only on authoritative values (cell id + spatial
information) over the analysis's declared cell ordering; it never depends on
dictionary iteration order, filesystem order, worker order, shard order, or
serialization order (``projection.md`` § "Deterministic selection").
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ehp_sn.figures import ResolvedFigureSelection

from ehp_research.analysis import HpcAnalysis

#: Canonical semantic identity of the top-spatial-information selection.
SELECTION_REF = "top-spatial-information-cells"
#: Version of the selection semantics defined in this module.
SELECTION_VERSION = 1


class CellSelectionError(ValueError):
    """A controlled failure of research-owned HPC cell selection."""


class DuplicateCellIdentityError(CellSelectionError):
    """The authoritative source violates the cell-identity uniqueness contract."""


@dataclass(frozen=True, slots=True)
class TopSpatialInformationCells:
    """Authored selection: the ``count`` valid cells with highest spatial information.

    ``count`` is the exact required cardinality. Candidates are the valid cells
    of the authoritative :class:`HpcAnalysis` (finite spatial information),
    ranked by ``spatial_information`` descending, ties broken by ``cell_id``
    ascending.

    The selector records the authored intent; :func:`resolve_top_spatial_information`
    turns it into an exact ``ResolvedFigureSelection`` against one authoritative
    source.
    """

    count: int

    def resolve(self, analysis: HpcAnalysis) -> ResolvedFigureSelection:
        """Resolve this authored selection against one authoritative analysis.

        Returns the exact ``ResolvedFigureSelection`` carrying the authored
        semantic identity/version, the authored parameters, and the exact ordered
        resolved cell identities. Raises a controlled :class:`CellSelectionError`
        when the source is insufficient, and a :class:`DuplicateCellIdentityError`
        when the authoritative source violates cell-identity uniqueness.
        """
        return resolve_top_spatial_information(analysis, self.count)


def _validate_cell_identity_uniqueness(analysis: HpcAnalysis) -> None:
    """Reject duplicate cell identity in the authoritative source.

    The authoritative analysis contract is the primary authority for cell
    identity; this defensive check surfaces a source-contract violation as a
    controlled failure rather than silently producing an ill-defined selection
    (P3-T4 · P3-T21). It is not an independent authority defining cell identity.
    """
    seen: set[str] = set()
    for cell in analysis.cells:
        if cell.cell_id in seen:
            raise DuplicateCellIdentityError(
                f"authoritative HPC analysis contains duplicate cell identity {cell.cell_id!r}"
            )
        seen.add(cell.cell_id)


def resolve_top_spatial_information(analysis: HpcAnalysis, count: int) -> ResolvedFigureSelection:
    """Deterministically resolve ``TopSpatialInformationCells(count=count)``.

    Uses only authoritative values (cell id, spatial information) in the
    analysis's declared cell order. Non-finite spatial-information values are
    excluded. If fewer than ``count`` valid cells remain, raises a controlled
    :class:`CellSelectionError` rather than silently returning fewer (P3-T4 ·
    P3-T21).
    """
    if count < 1:
        raise CellSelectionError(f"TopSpatialInformationCells count must be >= 1, got {count}")
    _validate_cell_identity_uniqueness(analysis)

    candidates = analysis.valid_cells()
    if len(candidates) < count:
        raise CellSelectionError(
            f"TopSpatialInformationCells(count={count}) requires {count} valid cells, "
            f"but the authoritative analysis provides only {len(candidates)}"
        )

    # Deterministic rank: spatial_information descending, cell_id ascending tie-break.
    ordered = sorted(
        candidates,
        key=lambda cell: (
            -cell.spatial_information if math.isfinite(cell.spatial_information) else math.inf,
            cell.cell_id,
        ),
    )
    selected = ordered[:count]
    resolved = tuple(cell.cell_id for cell in selected)
    return ResolvedFigureSelection(
        selection_ref=SELECTION_REF,
        selection_version=SELECTION_VERSION,
        parameters={"count": count},
        resolved_identities=resolved,
    )


__all__ = [
    "CellSelectionError",
    "DuplicateCellIdentityError",
    "SELECTION_REF",
    "SELECTION_VERSION",
    "TopSpatialInformationCells",
    "resolve_top_spatial_information",
]
