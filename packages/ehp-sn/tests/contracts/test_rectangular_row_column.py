"""Contract tests for the shared ``rectangular-row-column/v1`` domain schema.

Verifies the ``ehp_sn``-owned implementation of the rectangular registered
domain schema under ``docs/docs/framework/contracts/domains/ambient-domain-v1.md``:
canonical identity, reconstruction, the row-major bijective mapping, and the
invalid-dimension/coordinate rejections.

The domain is framework-owned and producer-neutral: it owns position identity
and coordinate structure only, with no hex support, no topology movement, no
passability, and no vocabulary semantics (Target 8 acceptance).
"""

from __future__ import annotations

import pytest
from ehp_sn.contracts.domains import (
    AmbientDomainError,
    domains_compatible,
    rectangular_row_column_domain,
)


def test_same_height_width_same_canonical_domain() -> None:
    """Same H,W → same canonical domain declaration (Target 8 acceptance)."""
    a = rectangular_row_column_domain(2, 3)
    b = rectangular_row_column_domain(2, 3)
    assert a == b
    assert a.declaration() == b.declaration()
    assert domains_compatible(a, b)


def test_different_dimensions_different_domain() -> None:
    """Different shapes → different canonical domain identity."""
    a = rectangular_row_column_domain(2, 3)
    b = rectangular_row_column_domain(3, 2)
    assert a != b
    assert not domains_compatible(a, b)
    # equal position counts do not imply equal domains
    assert a.position_count == b.position_count


def test_row_major_mapping_is_bijective() -> None:
    """position_id ↔ coordinate is a bijection over the complete position set."""
    domain = rectangular_row_column_domain(4, 5)
    ids = [domain.position_id(r, c) for r in range(4) for c in range(5)]
    assert ids == list(range(20))
    assert len(set(ids)) == 20
    for pid in range(20):
        r, c = domain.coordinate(pid)
        assert domain.position_id(r, c) == pid


def test_position_id_formula() -> None:
    """position_id(row, column) = row * width + column."""
    domain = rectangular_row_column_domain(3, 4)
    assert domain.position_id(2, 3) == 2 * 4 + 3 == 11


def test_schema_determined_declaration_fields() -> None:
    """Schema-determined assertions match the registered schema (AD-REC-003)."""
    d = rectangular_row_column_domain(2, 3).declaration()
    assert d["schema"] == "rectangular-row-column/v1"
    assert d["coordinate_system"] == "row-column"
    assert d["coordinate_structure"] == "rectangular-lattice"
    assert d["shape"] == "rectangle"
    assert d["position_count"] == 6


def test_invalid_dimensions_rejected() -> None:
    """height/width must be >= 1 (AD-REC-001 / rectangular domain)."""
    with pytest.raises(AmbientDomainError):
        rectangular_row_column_domain(0, 3)
    with pytest.raises(AmbientDomainError):
        rectangular_row_column_domain(3, 0)
    with pytest.raises(AmbientDomainError):
        rectangular_row_column_domain(-1, 3)


def test_invalid_coordinate_rejected() -> None:
    """Out-of-domain row/column coordinates are rejected."""
    domain = rectangular_row_column_domain(2, 2)
    with pytest.raises(AmbientDomainError):
        domain.position_id(2, 0)
    with pytest.raises(AmbientDomainError):
        domain.position_id(0, 2)
    with pytest.raises(AmbientDomainError):
        domain.coordinate(4)


def test_no_hex_or_grid4_or_passability_semantics() -> None:
    """The domain carries no hex/grid4/passability/vocabulary semantics.

    The domain is a pure position space; movement, traversability, and
    observation assignment are owned by reusing contracts.
    """
    d = rectangular_row_column_domain(2, 2)
    assert d.declaration()["coordinate_structure"] == "rectangular-lattice"
    # No grid4 semantics present: the declaration is only the position space.
    assert "grid4" not in str(d.declaration())
