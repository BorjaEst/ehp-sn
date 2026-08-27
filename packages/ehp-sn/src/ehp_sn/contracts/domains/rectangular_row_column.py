"""Shared rectangular row-column ambient domain (``rectangular-row-column/v1``).

This module is the ``ehp_sn``-owned implementation of the rectangular registered
domain schema under the framework contract
``docs/docs/framework/contracts/domains/ambient-domain-v1.md``.

It defines the canonical position space shared by contracts that reuse an
ambient domain — for example ``categorical-field/v1`` and ``raster-topology/v1``
— so that a topology record and a field record can be checked for domain
compatibility against one shared schema.

The domain owns **position identity and coordinate structure only**. It does not
define movement, admissible transitions, walls, blocked cells, passability, or
any observation assignment — those belong to the reusing contracts
(``ambient-domain/v1`` § "Position identity is not movement").

Canonical semantics:

.. code-block:: text

    schema:               rectangular-row-column/v1
    coordinate_system:    row-column
    shape:                rectangle
    coordinate_structure: rectangular-lattice
    height:               H >= 1
    width:                W >= 1
    D = {(r, c) | 0 <= r < H and 0 <= c < W}
    position_count = H * W
    position_id(r, c) = r * W + c
    canonical enumeration = row-major by increasing position_id

It is framework-owned and producer-neutral: the constructor accepts only
contract-owned authoritative inputs (``height`` and ``width``), and there is no
hexagon, grid4 movement, passability, or vocabulary semantics anywhere here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

#: The canonical registered domain-schema reference.
SCHEMA_REF: Final = "rectangular-row-column/v1"
#: The ambient-domain declaration schema this registered schema embeds.
AMBIENT_DOMAIN_SCHEMA_REF: Final = "ambient-domain/v1"
#: Schema-determined coordinate convention.
COORDINATE_SYSTEM: Final = "row-column"
#: Schema-determined shape classification.
SHAPE: Final = "rectangle"
#: Schema-determined geometric coordinate structure.
COORDINATE_STRUCTURE: Final = "rectangular-lattice"


class AmbientDomainError(ValueError):
    """A supplied domain does not conform to ``rectangular-row-column/v1``.

    Raised for invalid dimensions or an out-of-range coordinate lookup. It is a
    contract-domain error; producers translate it at their own layer.
    """


def _validate_dimensions(height: int, width: int) -> None:
    """Raise :class:`AmbientDomainError` unless ``height``/``width`` are valid."""
    if not isinstance(height, int) or isinstance(height, bool):
        raise AmbientDomainError(f"height must be an integer, got {type(height).__name__}")
    if not isinstance(width, int) or isinstance(width, bool):
        raise AmbientDomainError(f"width must be an integer, got {type(width).__name__}")
    if height < 1:
        raise AmbientDomainError(f"height must be >= 1, got {height}")
    if width < 1:
        raise AmbientDomainError(f"width must be >= 1, got {width}")


@dataclass(frozen=True, slots=True)
class RectangularRowColumnDomain:
    """An immutable, conforming ``rectangular-row-column/v1`` domain declaration.

    ``height`` and ``width`` are the authoritative schema-specific shape
    parameters. ``position_count`` is the derived assertion ``H * W``; the
    schema-determined assertions (``coordinate_system``, ``shape``,
    ``coordinate_structure``) are fixed by the registered schema
    (``AD-REC-002``/``AD-REC-003``).

    The canonical position enumeration is row-major by increasing ``position_id``.
    """

    height: int
    width: int

    @property
    def schema_ref(self) -> str:
        """The canonical registered domain-schema reference."""
        return SCHEMA_REF

    @property
    def ambient_schema_ref(self) -> str:
        """The ambient-domain declaration schema reference."""
        return AMBIENT_DOMAIN_SCHEMA_REF

    @property
    def coordinate_system(self) -> str:
        """Schema-determined coordinate convention."""
        return COORDINATE_SYSTEM

    @property
    def shape(self) -> str:
        """Schema-determined shape classification."""
        return SHAPE

    @property
    def coordinate_structure(self) -> str:
        """Schema-determined geometric coordinate structure."""
        return COORDINATE_STRUCTURE

    @property
    def position_count(self) -> int:
        """Derived number of canonical positions (``H * W``)."""
        return self.height * self.width

    def position_id(self, row: int, column: int) -> int:
        """Return the canonical dense position ID for a row/column coordinate.

        ``position_id(row, column) = row * width + column``
        (``ambient-domain/v1``). Raises :class:`AmbientDomainError` for a
        coordinate outside the domain.
        """
        if not 0 <= row < self.height:
            raise AmbientDomainError(f"row {row} outside domain height [0, {self.height})")
        if not 0 <= column < self.width:
            raise AmbientDomainError(f"column {column} outside domain width [0, {self.width})")
        return row * self.width + column

    def coordinate(self, position_id: int) -> tuple[int, int]:
        """Return the ``(row, column)`` coordinate for a canonical position ID.

        Inverse of :func:`position_id`; the mapping is bijective over
        ``{0, ..., position_count - 1}``. Raises :class:`AmbientDomainError` for
        an out-of-range position ID.
        """
        if not 0 <= position_id < self.position_count:
            raise AmbientDomainError(
                f"position_id {position_id} outside domain [0, {self.position_count})"
            )
        return divmod(position_id, self.width)

    def declaration(self) -> dict[str, object]:
        """Return the complete canonical domain declaration.

        Sufficient to reconstruct the full position set and canonical order
        without another artifact (``AD-REC-001``).
        """
        return {
            "schema": SCHEMA_REF,
            "coordinate_system": COORDINATE_SYSTEM,
            "coordinate_structure": COORDINATE_STRUCTURE,
            "shape": SHAPE,
            "height": self.height,
            "width": self.width,
            "position_count": self.position_count,
        }


def rectangular_row_column_domain(height: int, width: int) -> RectangularRowColumnDomain:
    """Construct a conforming ``rectangular-row-column/v1`` domain.

    Accepts only contract-owned authoritative inputs: ``height`` and ``width``.
    Validates the dimensions and returns an immutable domain.
    """
    _validate_dimensions(height, width)
    return RectangularRowColumnDomain(height=height, width=width)


def domains_compatible(a: RectangularRowColumnDomain, b: RectangularRowColumnDomain) -> bool:
    """Whether two domains are domain-identical.

    Domain identity is complete-declaration equality under the registered schema
    (``ambient-domain/v1``): equal position counts alone are insufficient.
    """
    return a == b


__all__ = [
    "AMBIENT_DOMAIN_SCHEMA_REF",
    "AmbientDomainError",
    "COORDINATE_STRUCTURE",
    "COORDINATE_SYSTEM",
    "RectangularRowColumnDomain",
    "SCHEMA_REF",
    "SHAPE",
    "domains_compatible",
    "rectangular_row_column_domain",
]
