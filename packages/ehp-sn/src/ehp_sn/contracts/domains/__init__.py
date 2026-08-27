"""Ambient spatial-domain contracts (``ehp_sn`` framework-owned).

Subpackage re-exports the registered ambient-domain schema implementations, for
example :class:`~ehp_sn.contracts.domains.rectangular_row_column.RectangularRowColumnDomain`.
The normative semantics live in
``docs/docs/framework/contracts/domains/ambient-domain-v1.md``.
"""

from __future__ import annotations

from .rectangular_row_column import (
    AMBIENT_DOMAIN_SCHEMA_REF,
    COORDINATE_STRUCTURE,
    COORDINATE_SYSTEM,
    SCHEMA_REF,
    SHAPE,
    AmbientDomainError,
    RectangularRowColumnDomain,
    domains_compatible,
    rectangular_row_column_domain,
)

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
