"""DungeonGen acceptance, deterministic retry/exhaustion, and duplicate policy.

This module owns the DungeonGen producer steps that decide whether a normalized
candidate topology is accepted:

* :data:`ACCEPTANCE_CONDITIONS` / :func:`evaluate` — the first acceptance policy
 : a named set of configured conditions, each of which can reject a
  candidate and is attributable as the rejection reason;
* :func:`run_candidate` / :func:`run_logical_topology` — the deterministic
  retry and exhaustion driver: attempt ``a`` ranges
  ``0 .. attempt_budget - 1``, candidate seeds are derived per index,
  and exhaustion fails the logical realization explicitly;
* the `allow` duplicate policy: independent outcomes remain
  separate records and repetition is detected/reported.

The first executable profile implements only ``allow``; a valid-but-unsupported
``reject-exact`` configuration is rejected by the resolver, never silently
downgraded.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .configuration import DungeonGenConfiguration
from .conversion import (
    ConversionError,
    convert_to_passability,
    largest_component,
    normalize_extent,
)
from .generation import (
    GenerationError,
    NativeCandidate,
    candidate_seed,
    generate_native,
)

#: A named acceptance condition: ``(name, check(height, width, states) -> bool)``.
AcceptanceCondition = tuple[str, Callable[[int, int, int], bool]]


class AcceptanceError(ValueError):
    """A controlled DungeonGen acceptance, retry, or exhaustion failure."""


@dataclass(frozen=True, slots=True)
class Rejection:
    """One rejected candidate attempt with its attributable reason."""

    attempt: int
    reason: str


@dataclass(frozen=True, slots=True)
class AcceptedTopology:
    """An accepted normalized topology realization (Targets 7-9).

    ``height``/``width``/``passable`` is the canonical normalized retained
    topology (extent + cell-wise passability) ready for the shared
    ``raster-topology/v1`` constructor. ``logical_index`` and ``attempt`` are
    the producer-owned lineage of this record; ``rejections`` are the prior
    rejected attempts for the same logical index with their reasons;
    ``duplicated`` reports (under the ``allow`` policy) that this canonical
    topology content repeated an earlier record's content.
    """

    logical_index: int
    attempt: int
    height: int
    width: int
    passable: tuple[bool, ...]
    rejections: tuple[Rejection, ...] = field(default_factory=tuple)
    duplicated: bool = False


# ---------------------------------------------------------------------------
# Acceptance policy
# ---------------------------------------------------------------------------


def _size_policy_conditions(
    configuration: DungeonGenConfiguration,
) -> tuple[AcceptanceCondition, ...]:
    """The configured extent/state-count acceptance conditions.

    Only the criteria actually declared by the resolved reusable policy are
    enforced; no invented quality/room/dead-end/corridor thresholds are added.
    """
    sp = configuration.size_policy

    def _height(h: int, _w: int, _s: int) -> bool:
        return sp.minimum_height <= h <= sp.maximum_height

    def _width(_h: int, w: int, _s: int) -> bool:
        return sp.minimum_width <= w <= sp.maximum_width

    def _states(_h: int, _w: int, s: int) -> bool:
        return sp.minimum_states <= s <= sp.maximum_states

    return (
        ("extent-min-height", _height),
        ("extent-max-height", _height),
        ("extent-min-width", _width),
        ("extent-max-width", _width),
        ("states-min", _states),
        ("states-max", _states),
    )


def evaluate(
    configuration: DungeonGenConfiguration, height: int, width: int, states: int
) -> tuple[str, ...]:
    """Return the names of the acceptance conditions the candidate fails (empty = pass).

    Every failed condition is attributable by name.
    Every rejection is attributable to a named configured acceptance condition.
    """
    failed: list[str] = []
    for name, check in _size_policy_conditions(configuration):
        if not check(height, width, states):
            failed.append(name)
    if configuration.require_connected and states < 1:
        failed.append("connected-nonempty")
    return tuple(failed)


# ---------------------------------------------------------------------------
# Candidate generation → conversion → component-select → normalize → accept
# ---------------------------------------------------------------------------


def _native_to_normalized(candidate: NativeCandidate) -> tuple[int, int, tuple[bool, ...]]:
    """Run conversion → component selection → re-normalization for one native candidate."""
    passable_native = convert_to_passability(candidate)
    height, width, raw_passable = normalize_extent(passable_native)
    return largest_component(height, width, raw_passable)


def run_logical_topology(
    configuration: DungeonGenConfiguration,
    logical_index: int,
    *,
    seen: set[tuple[int, int, tuple[bool, ...]]] | None = None,
    generator: Callable[[DungeonGenConfiguration, int], NativeCandidate] = generate_native,
) -> AcceptedTopology | RejectionReason:
    """Generate and accept one logical topology index under the retry budget.

    Attempts run ``a = 0 .. attempt_budget - 1``. For each attempt it derives
    the candidate seed, generates, converts, component-selects,
    normalizes, and evaluates acceptance (Targets 5-8). Under the ``allow``
    duplicate policy the candidate is accepted regardless of content repetition,
    and any repetition of an earlier canonical topology is reported.

    On exhaustion it returns a :class:`RejectionReason` describing the logical
    index and the per-attempt rejection reasons; it never borrows a candidate
    seed from another index and never silently substitutes another realization
    index.
    """
    seen = seen if seen is not None else set()
    rejections: list[Rejection] = []
    for attempt in range(configuration.attempt_budget):
        seed = candidate_seed(configuration, logical_index, attempt)
        try:
            candidate = generator(configuration, seed)
            height, width, passable = _native_to_normalized(candidate)
            states = sum(1 for p in passable if p)
            failed = evaluate(configuration, height, width, states)
            if failed:
                rejections.append(Rejection(attempt=attempt, reason=";".join(failed)))
                continue
            key = (height, width, passable)
            duplicated = key in seen
            seen.add(key)
            return AcceptedTopology(
                logical_index=logical_index,
                attempt=attempt,
                height=height,
                width=width,
                passable=passable,
                rejections=tuple(rejections),
                duplicated=duplicated,
            )
        except (ConversionError, GenerationError) as exc:
            rejections.append(
                Rejection(attempt=attempt, reason=f"candidate-failure:{exc.__class__.__name__}")
            )
            continue
    return RejectionReason(logical_index=logical_index, rejections=tuple(rejections))


@dataclass(frozen=True, slots=True)
class RejectionReason:
    """The explicit exhaustion outcome for one logical topology index."""

    logical_index: int
    rejections: tuple[Rejection, ...]

    @property
    def message(self) -> str:
        reasons = "; ".join(f"attempt {r.attempt}: {r.reason}" for r in self.rejections)
        return (
            f"DungeonGen exhaustion for logical topology index {self.logical_index}: "
            f"no accepted candidate within the attempt budget. Rejections: {reasons}"
        )


__all__ = [
    "AcceptanceCondition",
    "AcceptanceError",
    "AcceptedTopology",
    "Rejection",
    "RejectionReason",
    "evaluate",
    "run_logical_topology",
]
