"""The immutable framework execution plan (Capability 6).

This module establishes the minimal, generic, immutable
:class:`ExecutionPlan` used to represent one fully resolved planning operation.
It is the first in-code instantiation of the documented immutable plan
(``docs/docs/interfaces/configuration/model.md`` § "ExecutionPlan",
``docs/docs/interfaces/configuration/resolution.md`` § "PLAN").

The plan is produced by planning orchestration and contains, for one selected
component:

* ``target`` — the selected canonical component reference;
* ``output_contract`` — the authoritative normalized output schema reference,
  derived from the registered definition (never a second authority);
* ``configuration`` — the producer-effective configuration, carried opaquely
  (the framework never inspects producer fields);
* ``resources`` — the exact bound resource records;
* ``identity_inputs`` — the producer-declared identity-bearing scientific
  inputs, canonical and ordered.

The plan is immutable and value-comparable: the same resolved components and
inputs yield an equal plan, and changing an identity-bearing input yields a
different plan. This is deliberately a plan of intention only: it performs no
generation, stages nothing, mutates no artifact, and commits nothing.
"""

from __future__ import annotations

from dataclasses import dataclass

from ehp_sn.experiments import ComponentRef

from .coordinates import ReleaseCoordinate
from .identity import IdentityInput
from .resources import ResolvedResource


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    """An immutable description of one fully resolved data-build operation.

    ``configuration`` is opaque to the framework: it is the producer-effective
    object exactly as the producer resolved it, and nothing here reads its
    fields.

    ``resources`` are already BOUND (exact logical references selected by the
    framework resource resolver); the plan does not contain DECLARED-only
    requirements.

    ``identity_inputs`` are the canonical, ordered identity-bearing inputs
    declared by the producer and incorporated into the plan by the framework.

    ``release_coordinate`` is the intended committed release coordinate resolved
    from framework artifact semantics (family + variant + configured release),
    when the producer declares a variant and the configuration declares a
    release. It is ``None`` when that information is not present. It is a
    framework-owned artifact coordinate, never supplied by the producer.

    Value equality is structural, so two plans built from the same resolved
    components and identity inputs compare equal, and a different
    identity-bearing input yields a different plan (no hashing is invented).
    """

    target: ComponentRef
    output_contract: str
    configuration: object
    resources: tuple[ResolvedResource, ...]
    identity_inputs: tuple[IdentityInput, ...]
    release_coordinate: ReleaseCoordinate | None = None


__all__ = ["ExecutionPlan"]
