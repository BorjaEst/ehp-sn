"""Framework planning-state classification for a release coordinate.

This module owns the *decision logic* that classifies a release coordinate's
physical state into the planning outcomes the artifact lifecycle defines
(``data-artifacts.md`` § "Planning states" and ``data-layout.md`` § "Planning
outcomes"):

```text
available            nothing committed at the destination
reusable             a valid committed artifact with the same build-input identity
conflict             a committed artifact with incompatible build-input identity
invalid existing     incomplete/corrupt content that is neither reusable nor safely available
```

The classification is a pure function over abstract facts (does a committed
artifact exist, and what build-input identity does it record) so it does not
depend on a particular physical backend. The physical inspection that produces
those facts is a framework artifact-store concern; this module only decides the
state. The check belongs in planning so that a build decides whether producer
execution is necessary **before** executing it.
"""

from __future__ import annotations

from enum import Enum


class PlanningState(Enum):
    """The planning classification of one release coordinate.

    ``AVAILABLE`` — nothing committed at the destination; build may proceed.
    ``REUSABLE`` — a valid committed artifact records the same build-input
    identity; the build may reuse it without producer execution.
    ``CONFLICT`` — a committed artifact occupies the coordinate with an
    incompatible build-input identity; the build must fail (never overwrite).
    ``INVALID_EXISTING_STATE`` — incomplete/corrupt content exists at the
    destination; it is neither reusable nor safely available.
    """

    AVAILABLE = "available"
    REUSABLE = "reusable"
    CONFLICT = "conflict"
    INVALID_EXISTING_STATE = "invalid_existing_state"


def classify_planning_state(
    *,
    committed_exists: bool,
    existing_build_input_identity: str | None,
    valid_existing: bool,
    planned_build_input_identity: str,
) -> PlanningState:
    """Classify a release coordinate's planning state from abstract facts.

    ``committed_exists`` is whether a committed artifact occupies the
    coordinate; ``valid_existing`` whether that content passes required
    integrity checks (TARGET: a corrupt/incomplete release is not treated as
    reusable or safely available); ``existing_build_input_identity`` is the
    recorded build-input identity of the existing committed artifact when one is
    present, else ``None``; ``planned_build_input_identity`` is the build-input
    identity of the intended build.

    Rules:

    * no committed content (``committed_exists`` false) and no invalid content
      → ``AVAILABLE``;
    * committed content that fails integrity → ``INVALID_EXISTING_STATE``;
    * committed, valid, same build-input identity → ``REUSABLE``;
    * committed, valid, different build-input identity → ``CONFLICT``.
    """
    if not committed_exists and valid_existing:
        return PlanningState.AVAILABLE
    if not valid_existing:
        return PlanningState.INVALID_EXISTING_STATE
    if existing_build_input_identity == planned_build_input_identity:
        return PlanningState.REUSABLE
    return PlanningState.CONFLICT


__all__ = ["PlanningState", "classify_planning_state"]
