"""Generic producer planning capability (Capability 6).

This module defines the narrow, demonstrated provider boundary that lets
``ehp_sn`` orchestrate planning for a registered substrate without ever
importing a concrete research package or inspecting a producer configuration
field (``ARCH-001`` / no research leakage).

The genuinely demonstrated producer-side operation (established by the first
two completed producer-configuration implementations) is:

.. code-block:: text

    generic loaded configuration document
            ↓
    producer-owned resolution + planning declaration
            ↓
    generic PlanningDeclaration

A :class:`SubstratePlanningCapability` is the framework-owned protocol a
producer objects to. It exposes exactly one operation at the planning boundary:
:meth:`~SubstratePlanningCapability.plan`. It deliberately does **not** expose
build, validate, inspect, execute, or any lifecycle verb — later capabilities
may add those as *independent* capabilities rather than widening this one, so
no monolithic provider interface is assumed (see ``docs/invariants.md`` ARCH-007
and the Capability-6 design notes).

The producer owns:

* WHAT the effective scientific configuration is;
* WHAT logical resources its build requires (including any upstream source
  requirement);
* WHAT scientific inputs are identity-bearing.

The framework owns:

* whether a planning capability is present for a registered definition;
* HOW resource requirements are bound and identity inputs are canonicalized and
  incorporated into the immutable plan.

Nothing here is substrate-family specific; ``ehp_sn`` never branches on a family.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from ehp_sn.configuration import LoadedConfiguration

from .identity import IdentityInput
from .resources import ResourceRequirement


@dataclass(frozen=True, slots=True)
class PlanningDeclaration:
    """A generic declaration of what the framework must resolve for one build.

    Produced by a producer capability and consumed by the framework planning
    orchestration. It carries the producer's effective scientific configuration
    (opaque to the framework) together with the logical resource requirements
    and identity-bearing scientific inputs that the framework must bind and
    incorporate.

    ``configuration`` is the immutable, fully effective producer configuration
    (for example a resolved substrate-family configuration). The framework
    never interprets its fields; it only carries it opaquely on the plan.

    ``resources`` are the logical resource *requirements* the producer declares
    — they are DECLARED, not yet BOUND. The framework resource resolver binds
    each into an exact :class:`~ehp_sn.planning.resources.ResolvedResource`.

    ``identity_inputs`` are the producer-declared scientific inputs that
    contribute to build identity, in a stable canonical order. The framework
    binds/incorporates them into the immutable plan; it does not reinterpret
    their meaning.
    """

    configuration: object
    resources: tuple[ResourceRequirement, ...] = ()
    identity_inputs: tuple[IdentityInput, ...] = field(default_factory=tuple)


@runtime_checkable
class SubstratePlanningCapability(Protocol):
    """Framework-owned boundary for a registered substrate's planning operation.

    A producer object (in ``ehp_research``) implements this protocol so the
    framework can plan for the definition it registers, without the framework
    importing the producer package by name.

    :meth:`plan` interprets a generic :class:`~ehp_sn.configuration.LoadedConfiguration`
    document (Capability 4) into a generic :class:`PlanningDeclaration`. It is
    a pure resolution/declaration operation: it performs no file loading beyond
    what the loader already did, no resource binding, no generation, and no
    artifact mutation.
    """

    def plan(self, document: LoadedConfiguration) -> PlanningDeclaration:
        """Resolve ``document`` and declare the generic planning inputs.

        Returns the producer's effective configuration, required logical
        resources, and identity-bearing scientific inputs as a generic
        :class:`PlanningDeclaration`.
        """
        ...


__all__ = ["PlanningDeclaration", "SubstratePlanningCapability"]
