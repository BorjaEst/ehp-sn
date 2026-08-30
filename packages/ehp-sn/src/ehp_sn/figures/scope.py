"""Figure source-scope vocabulary (Phase 4).

A figure source has a granularity: it is either exactly one committed logical
record (``record``) or a committed artifact's collection of records conforming
to a declared logical contract (``artifact``). This is generic framework
vocabulary shared by the figure requirement contract and the projection source
binding (Phase-4 § 4.1, § 20); it is not producer, contract, or storage detail.

This module is a leaf with no figure imports so both ``contracts.py`` and
``projection.py`` can consume the constants without a circular dependency.
"""

from __future__ import annotations

#: A figure source scoped to exactly one committed logical record
#: (``scope: record``).
SCOPE_RECORD = "record"

#: A figure source scoped to a committed artifact's collection of records
#: conforming to a declared logical contract (``scope: artifact``).
SCOPE_ARTIFACT = "artifact"

#: The ordinary source-scope vocabulary for a ``FigureInputRequirement``.
SOURCE_SCOPES: frozenset[str] = frozenset({SCOPE_RECORD, SCOPE_ARTIFACT})

__all__ = ["SCOPE_ARTIFACT", "SCOPE_RECORD", "SOURCE_SCOPES"]
