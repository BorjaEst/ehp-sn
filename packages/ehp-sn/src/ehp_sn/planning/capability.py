"""Generic producer planning operation and its declaration.

This module defines the narrow, demonstrated producer operation that lets
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

It is represented by the single typed callable :data:`PlanningResolver`
(``Callable[[LoadedConfiguration], PlanningDeclaration]``). A producer supplies
one such callable per registered definition; the planning composition binds it
to the authoritative definition object. No protocol object, capability slot, or
lifecycle verb is introduced: planning needs exactly this one resolution and
declaration operation, and nothing more (no build / validate / inspect /
execute reservation).

The producer owns:

* WHAT the effective scientific configuration is;
* WHAT logical resources its build requires (including any upstream source
  requirement);
* WHAT scientific inputs are identity-bearing.

The framework owns:

* whether a planning resolver is present for a registered definition;
* HOW resource requirements are bound and identity inputs are canonicalized and
  incorporated into the immutable plan.

Nothing here is substrate-family specific; ``ehp_sn`` never branches on a family.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from ehp_sn.configuration import LoadedConfiguration

from .identity import IdentityInput
from .resources import ResourceRequirement


@dataclass(frozen=True, slots=True)
class PlanningDeclaration:
    """A generic declaration of what the framework must resolve for one build.

    Produced by a producer planning resolver and consumed by the framework
    planning orchestration. It carries the producer's effective scientific
    configuration (opaque to the framework) together with the logical resource
    requirements and identity-bearing scientific inputs that the framework must
    bind and incorporate.

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


#: The typed producer planning operation bound to a registered definition.
#:
#: It interprets a generic :class:`~ehp_sn.configuration.LoadedConfiguration`
#: document into a generic :class:`PlanningDeclaration`, performing producer
#: configuration resolution and planning-input declaration. The behavioral
#: contract is typed (a callable with an exact signature); only the producer
#: result it returns is deliberately opaque to the framework.
type PlanningResolver = Callable[[LoadedConfiguration], PlanningDeclaration]


__all__ = ["PlanningDeclaration", "PlanningResolver"]
