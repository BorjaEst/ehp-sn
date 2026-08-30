"""Shared rectangular-domain realization (Phase 2).

This module is the one canonical framework implementation of the scientific
position → (row, column) → matrix realization for figures that visualize an
ambient domain declared as ``rectangular-row-column/v1`` (Phase-2 § 6).

```text
same ambient-domain declaration
        ↓
same scientific row/column mapping
```

across every figure that visualizes it. ``raster-topology-inspection/v1`` and
``categorical-field-inspection/v1`` both reshape their canonical row-major
value array into a ``(height, width)`` matrix through :func:`to_matrix`, which
is derived from the contract's own canonical position mapping
(``position_id(r, c) = r * width + c`` on
:class:`~ehp_sn.contracts.domains.RectangularRowColumnDomain`).

The principle (Phase-2 § 6 required invariant):

```text
do not maintain separate scientific reshaping logic in
    raster plotting
    categorical plotting
```

A different *drawing helper* is acceptable; a different *position-semantic
implementation* is not.
"""

from __future__ import annotations

from collections.abc import Sequence

from ehp_sn.contracts.domains import RectangularRowColumnDomain


def to_matrix[T](domain: RectangularRowColumnDomain, values: Sequence[T]) -> list[list[T]]:
    """Reshape a canonical row-major value array into a ``(height, width)`` matrix.

    ``values`` is the canonical value array in increasing ``position_id`` order
    (``values[position_id(r, c)]``), matching the domain's canonical row-major
    enumeration. The returned matrix is organized as ``matrix[row][column]``
    with the contract's canonical orientation:

    ```text
    matrix[r][c] == values[position_id(r, c)] == values[r * width + c]
    ```

    This is the single scientific row/column mapping shared by every rectangular
    figure realization (Phase-2 § 6). It performs no transpose, no reflection,
    and no reordering beyond the contract's canonical mapping.

    Raises :class:`ValueError` if ``values`` does not have exactly
    ``domain.position_count`` entries.
    """
    if len(values) != domain.position_count:
        raise ValueError(
            f"value array length {len(values)} != position_count {domain.position_count} "
            f"for {domain.schema_ref} domain"
        )
    height, width = domain.height, domain.width
    matrix: list[list[T]] = []
    for row in range(height):
        row_start = row * width
        matrix.append(list(values[row_start : row_start + width]))
    return matrix


__all__ = ["to_matrix"]
