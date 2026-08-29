"""Authoritative HPC place-field analysis result (Phase 3).

This module represents the **already-computed, authoritative** HPC spatial
analysis result that the Phase-3 HPC place-summary figure consumes. It is a
readable, stable, point-in-time representation of upstream scientific analysis
output; it never recomputes the quantities it carries.

The analysis result carries, for a population of cells:

```text
cell identity
spatial_information (bits / spike, per cell)
rate map (per cell, over one shared spatial domain)
field centre (per cell, one coordinate in that domain)
valid-cell semantics and population membership
spatial-domain semantics (extent, axis/coordinate convention, units)
```

``HpcAnalysis`` is a frozen, immutable value that owns its data. Rate maps are
stored as flat immutable tuples of floats together with an explicit shape, so
the value remains hashable and JSON-canonicalization-friendly without depending
on NumPy array identity or shared writable backing storage.

This is authoritative scientific content: downstream figure preparation reads
and selects from it but never estimates rate maps, computes spatial
information, or calculates field centres (``docs/invariants.md`` FIG-002;
P3-T6/P3-T23). Constructors are provided for producing the value from an
upstream analysis; they perform no scientific transformation.
"""

from __future__ import annotations

from dataclasses import dataclass

_ROW_AXIS = "y"
_COL_AXIS = "x"
_ORIGIN = "lower_left"


@dataclass(frozen=True, slots=True)
class HpcRateMapDomain:
    """Authoritative spatial-domain semantics shared by every population rate map.

    Declares the environment extent, the axis/coordinate convention of the rate
    maps, and the units/normalization state so that downstream rendering can
    interpret rate-map positions without guessing (P3-T2 · P3-T9). It is
    authoritative analysis metadata, not figure presentation policy.

    ``height``/``width`` are the rate-map array shape in rows/columns; the row
    axis is the spatial ``y`` axis and the column axis is the spatial ``x``
    axis, with origin at the lower-left of the environment.
    """

    height: int
    width: int
    spatial_extent_x: float
    spatial_extent_y: float
    unit: str = "spikes_per_second"

    def row_col_to_xy(self, row: float, col: float) -> tuple[float, float]:
        """Map a rate-map (row, col) coordinate to spatial ``(x, y)``.

        Uses the authoritative convention (rows index ``y``, columns index
        ``x``, origin at lower-left) and the declared spatial extent. This is a
        coordinate-convention derivation, not new scientific content.
        """
        x = self.spatial_extent_x * (col + 0.5) / self.width
        y = self.spatial_extent_y * (row + 0.5) / self.height
        return (x, y)

    @property
    def row_axis(self) -> str:
        """The spatial axis indexed by rate-map rows."""
        return _ROW_AXIS

    @property
    def col_axis(self) -> str:
        """The spatial axis indexed by rate-map columns."""
        return _COL_AXIS

    @property
    def origin(self) -> str:
        """The coordinate origin convention of the rate maps."""
        return _ORIGIN


@dataclass(frozen=True, slots=True)
class HpcCell:
    """One cell's authoritative place-field analysis record.

    ``rate_map`` is a flat tuple of ``domain.height * domain.width`` floats in
    row-major order; ``field_centre`` is the authoritative ``(row, col)``
    coordinate of the cell's place field. All values are already-computed
    authoritative results.
    """

    cell_id: str
    spatial_information: float
    rate_map: tuple[float, ...]
    field_centre: tuple[int, int]


@dataclass(frozen=True, slots=True)
class HpcAnalysis:
    """The authoritative HPC place-field analysis result for one population.

    ``domain`` carries the shared spatial-domain semantics; ``cells`` is the
    ordered population of cells in ``cell_id`` order. Only cells flagged
    ``valid`` participate in scientific selection/preparation for the
    place-summary figure (P3-T4). The value is immutable and owns its data.
    """

    domain: HpcRateMapDomain
    cells: tuple[HpcCell, ...]

    def valid_cells(self) -> tuple[HpcCell, ...]:
        """The eligible population: cells with a valid spatial-information value.

        A cell is eligible when its ``spatial_information`` is finite. This is
        the authoritative valid-cell semantics used by selection (P3-T4):
        selection never re-derives validity from array shape or layout.
        """
        import math

        return tuple(cell for cell in self.cells if math.isfinite(cell.spatial_information))


def hpc_analysis(
    *,
    height: int,
    width: int,
    spatial_extent_x: float,
    spatial_extent_y: float,
    cell_ids: tuple[str, ...],
    spatial_information: tuple[float, ...],
    rate_maps: tuple[tuple[float, ...], ...],
    field_centres: tuple[tuple[int, int], ...],
    unit: str = "spikes_per_second",
) -> HpcAnalysis:
    """Construct an authoritative :class:`HpcAnalysis` from upstream analysis output.

    Validates cardinality alignment between the cell identity, spatial
    information, rate-map, and field-centre sequences and the declared domain.
    This constructor performs validation / shape alignment only — it computes no
    scientific quantity.
    """
    domain = HpcRateMapDomain(
        height=int(height),
        width=int(width),
        spatial_extent_x=float(spatial_extent_x),
        spatial_extent_y=float(spatial_extent_y),
        unit=unit,
    )
    rate_map_cells = int(height) * int(width)
    if not (len(cell_ids) == len(spatial_information) == len(rate_maps) == len(field_centres)):
        raise ValueError(
            "hpc analysis cell cardinality mismatch: cell_ids, spatial_information, "
            "rate_maps and field_centres must have equal length"
        )
    cells: list[HpcCell] = []
    for cell_id, si, rate_map, centre in zip(
        cell_ids, spatial_information, rate_maps, field_centres, strict=True
    ):
        if len(rate_map) != rate_map_cells:
            raise ValueError(
                f"cell {cell_id!r} rate_map has {len(rate_map)} values, expected {rate_map_cells}"
            )
        if not (isinstance(centre[0], int) and isinstance(centre[1], int)):
            raise ValueError(f"cell {cell_id!r} field_centre must contain integers")
        cells.append(
            HpcCell(
                cell_id=str(cell_id),
                spatial_information=float(si),
                rate_map=tuple(float(v) for v in rate_map),
                field_centre=(int(centre[0]), int(centre[1])),
            )
        )
    return HpcAnalysis(domain=domain, cells=tuple(cells))


__all__ = [
    "HpcAnalysis",
    "HpcCell",
    "HpcRateMapDomain",
    "hpc_analysis",
]
