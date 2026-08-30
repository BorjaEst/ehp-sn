"""Deterministic inspection descriptor selection (Phase 4).

Phase-4 artifact summaries consume a collection of contract-conforming records
and produce deterministic inspection descriptors plus a deterministic
representative gallery. This module owns the **generic, producer- and
contract-neutral** selection mechanics (Phase-4 § 21-23): turning a candidate
population ordered by an exact inspection descriptor into a deterministic
representative selection.

Contract-specific descriptor *definitions* (e.g. ``edge_density`` for
``simple-digraph/v1``, ``passable_fraction`` for ``raster-topology/v1``,
``vocabulary_utilization`` for ``categorical-field/v1``) live with their owning
FigureSpec; this module provides only the reusable ordering/selection
machinery they share (Phase-4 § 32: generic helpers only where reuse is
demonstrated).

## Determinism contract (Phase-4 § 22-23)

A representative selection must define, for every rule that can affect the
result:

```text
candidate population
descriptor (per candidate)
ordering (ascending / descending)
cardinality
tie-breaking
missing values
non-finite values
duplicate handling
```

Stable record identity is the default final tie-break, so two records with
exactly equal descriptors are ordered deterministically by their canonical
``record_id``. No incidental artifact enumeration order, filesystem order, dict
order, or worker completion order may influence the result (Phase-4 § 23).

A descriptor ``None`` or non-finite value is handled by an explicit policy
(default: ranked after every finite value, then by record identity) rather than
an undefined comparison, so ordering is total and never raises (Phase-4 § 22).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

#: Ordering directions for a representative selection.
ORDER_ASCENDING = "ascending"
ORDER_DESCENDING = "descending"

#: Where a missing (``None``) descriptor value is ranked.
MISSING_LAST = "last"
MISSING_FIRST = "first"

#: Where a non-finite (NaN / ±inf) descriptor value is ranked.
NON_FINITE_LAST = "last"
NON_FINITE_FIRST = "first"


@dataclass(frozen=True, slots=True)
class SelectionCandidate:
    """One representative-selection candidate.

    ``record_id`` is the exact stable record identity (the final tie-break);
    ``descriptor`` is the exact inspection descriptor for this record, or
    ``None`` when the descriptor is missing for this candidate (handled by the
    explicit missing policy).
    """

    record_id: str
    descriptor: float | int | None


def rank_candidates(
    candidates: Sequence[SelectionCandidate],
    *,
    order: str = ORDER_ASCENDING,
    missing_policy: str = MISSING_LAST,
    non_finite_policy: str = NON_FINITE_LAST,
) -> tuple[SelectionCandidate, ...]:
    """Return a deterministic total ordering of ``candidates``.

    Primary sort key: the inspection descriptor. Secondary (final tie-break)
    key: the stable canonical record identity, so equal descriptors resolve
    deterministically and independent of incidental candidate enumeration
    order (Phase-4 § 23).

    ``order`` is ``ascending`` (smallest descriptor first) or ``descending``
    (largest descriptor first). ``missing_policy`` / ``non_finite_policy``
    place ``None`` / non-finite descriptor values before or after every finite
    value. Within the missing/non-finite classes, record identity still orders
    deterministically. The ordering is total and never raises on a comparison
    (Phase-4 § 22).
    """
    if order not in (ORDER_ASCENDING, ORDER_DESCENDING):
        raise ValueError(f"unknown ordering {order!r} (expected ascending|descending)")
    if missing_policy not in (MISSING_LAST, MISSING_FIRST):
        raise ValueError(f"unknown missing policy {missing_policy!r} (expected last|first)")
    if non_finite_policy not in (NON_FINITE_LAST, NON_FINITE_FIRST):
        raise ValueError(f"unknown non-finite policy {non_finite_policy!r} (expected last|first)")

    missing_rank = 1 if missing_policy == MISSING_FIRST else 2
    non_finite_rank = 1 if non_finite_policy == NON_FINITE_FIRST else 2
    finite_rank = 0 if (missing_policy == MISSING_LAST and non_finite_policy == NON_FINITE_LAST) else 3

    def sort_key(candidate: SelectionCandidate) -> tuple[int, float, str]:
        d = candidate.descriptor
        if d is None:
            group = missing_rank
            value = math.inf
        elif not math.isfinite(float(d)):
            group = non_finite_rank
            value = math.inf
        else:
            group = finite_rank
            value = float(d)
        if order == ORDER_DESCENDING and group == finite_rank:
            # Largest descriptor first.
            return (group, -value, candidate.record_id)
        return (group, value, candidate.record_id)

    return tuple(sorted(candidates, key=sort_key))


def select_representatives(
    candidates: Sequence[SelectionCandidate],
    *,
    k: int,
    order: str = ORDER_ASCENDING,
    missing_policy: str = MISSING_LAST,
    non_finite_policy: str = NON_FINITE_LAST,
) -> tuple[str, ...]:
    """Deterministically select up to ``k`` representative record identities.

    Ranks the candidate population with :func:`rank_candidates`, then takes the
    first ``min(k, len(candidates))`` identities in that total order. ``k``
    must be non-negative. The result is the exact deterministic representative
    selection provenance (Phase-4 § 23); the same collection under a different
    incidental enumeration order yields the same representative identities.
    """
    if k < 0:
        raise ValueError(f"representative cardinality must be non-negative, got {k}")
    if k == 0:
        return ()
    ranked = rank_candidates(
        candidates,
        order=order,
        missing_policy=missing_policy,
        non_finite_policy=non_finite_policy,
    )
    return tuple(candidate.record_id for candidate in ranked[:k])


__all__ = [
    "MISSING_FIRST",
    "MISSING_LAST",
    "NON_FINITE_FIRST",
    "NON_FINITE_LAST",
    "ORDER_ASCENDING",
    "ORDER_DESCENDING",
    "SelectionCandidate",
    "rank_candidates",
    "select_representatives",
]
