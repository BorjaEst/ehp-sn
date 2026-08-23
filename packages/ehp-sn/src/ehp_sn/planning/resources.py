"""Generic logical resource requirements and their resolution (Capability 6).

This module establishes the minimal generic framework representation for
logical resource requirements declared by a producer and the exact binding the
framework resolves them to. It is the first in-code instantiation of the
documented resource-requirement contract
(``docs/docs/interfaces/configuration/resource-requirements.md``), sized to the
genuinely demonstrated need of the first two planners (one declares no
resources; the other declares one upstream source requirement).

It is deliberately generic and small:

* a :class:`ResourceRequirement` is the *declared* requirement (the
  ``DECLARED`` state in the resource-requirements model) — it states *what* an
  exact logical resource is needed for, and the exact declared reference when
  the producer requires a specific one;
* a :class:`ResolvedResource` is the *bound* result (the ``BOUND`` state) — the
  exact logical resource reference selected for the requirement and the
  resolution source that produced it.

The framework owns the resolution boundary, never the family. A producer with
no resource need declares an empty ``resources`` tuple, so the planner performs
no family-specific branch.

Here "resolve" means selecting/recording the exact logical resource reference
for a declared requirement — not downloading, fetching, or acquiring external
data (``docs/invariants.md`` and Capability-6 design note §16). If a *required*
requirement cannot be bound to an exact reference, planning fails cleanly rather
than inventing a downloader.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

#: A requirement that must bind to exactly one logical resource.
CARDINALITY_ONE = "one"
#: A requirement that binds to exactly one logical resource or an explicit absent.
CARDINALITY_OPTIONAL_ONE = "optional-one"


class ResourceResolutionError(Exception):
    """A declared resource requirement could not be bound to an exact reference.

    Raised by a resource resolver when a *required* requirement cannot be
    resolved; a controlled framework planning failure, not a producer error.
    """


@dataclass(frozen=True, slots=True)
class ResourceRequirement:
    """A producer-declared logical resource requirement (DECLARED).

    Represents the requirement state, not the bound result. It states:

    * ``ref`` — the canonical requirement reference;
    * ``resource_kind`` — the category of resource required;
    * ``accepted_schema_ids`` — schema references the resource must conform to;
    * ``cardinality`` — ``one`` or ``optional-one``;
    * ``definition_resource_ref`` — the exact logical resource reference the
      producer requires, when known (for example an upstream source); ``None``
      when the exact reference must come from request/workspace binding;
    * ``description`` — a concise description of what the resource is for.

    This carries no physical location and performs no lookup.
    """

    ref: str
    resource_kind: str
    accepted_schema_ids: tuple[str, ...]
    cardinality: str
    definition_resource_ref: str | None
    description: str


@dataclass(frozen=True, slots=True)
class ResolvedResource:
    """An exact bound resource record (BOUND) for one requirement.

    The framework resource resolver produces this from a :class:`ResourceRequirement`.
    ``resource_ref`` is the exact logical resource reference selected;
    ``resolution_source`` records where it came from (for example ``definition``).
    """

    requirement_ref: str
    resource_ref: str
    resolution_source: str


@runtime_checkable
class ResourceResolver(Protocol):
    """Framework-owned boundary that binds resource requirements to exact references.

    Implementations resolve a :class:`ResourceRequirement` into an exact
    :class:`ResolvedResource`. They are framework/generic machinery, not
    producer or family specific.
    """

    def resolve(self, requirement: ResourceRequirement) -> ResolvedResource:
        """Return the exact bound resource for ``requirement``.

        Raises :class:`ResourceResolutionError` when a required requirement has
        no exact reference to bind.
        """
        ...


__all__ = [
    "CARDINALITY_ONE",
    "CARDINALITY_OPTIONAL_ONE",
    "ResolvedResource",
    "ResourceResolutionError",
    "ResourceRequirement",
    "ResourceResolver",
]
