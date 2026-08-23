"""Generic substrate planning orchestration (Capability 6).

This module owns the single generic orchestration function that connects a
registered substrate definition and its producer capability to the framework
resource-resolution and immutable-plan machinery, for one planning operation:

.. code-block:: text

    registered substrate definition
            +
        loaded configuration document
            ↓
        producer capability (plan)
            ↓
        producer-declared planning inputs
            ↓
        framework resource resolution
            ↓
        framework identity-input incorporation
            ↓
        existing immutable framework plan
            ↓
        STOP

:func:`plan_substrate` is a single function, not a service class. It is usable
independently of the CLI (a Python caller passes the registry, target, document,
and resource resolver), which matches the framework's Python/CLI equivalence
model. It must remain the *only* way a data build is planned.

The orchestration is pure resolution/construction relative to the artifact
lifecycle: it opens no TOML file, interprets no producer configuration field,
generates no records, invokes no producer generation, creates no output or
staging directory, stages nothing, and commits/manifests nothing. Planning
never receives artifact-store, staging, or generation dependencies.
"""

from __future__ import annotations

from typing import Protocol, cast

from ehp_sn.configuration import LoadedConfiguration
from ehp_sn.discovery import ComponentRegistry
from ehp_sn.experiments import ComponentRef

from .capability import SubstratePlanningCapability
from .plan import ExecutionPlan
from .resources import ResolvedResource, ResourceResolver

#: The component kind this planning path accepts.
_SUBSTRATE_KIND = "substrate"


class PlanningError(Exception):
    """A controlled framework planning failure.

    Raised when planning cannot construct an immutable plan: the target is not
    a registered substrate, no planning capability is registered for it, a
    registered producer cannot resolve the document into a declaration, or a
    required resource cannot be bound. It is a framework-domain error, not a
    CLI category; the CLI maps it at its own layer.
    """


class MissingPlanningCapabilityError(PlanningError):
    """The target definition has no registered planning capability."""


class NotASubstrateError(PlanningError):
    """Planning was requested for a component that is not a substrate."""


class ProducerResolutionError(PlanningError):
    """A registered producer could not resolve the document into a plan declaration.

    Raised when a registered producer's
    :meth:`~ehp_sn.planning.capability.SubstratePlanningCapability.plan` fails
    while interpreting a loaded configuration into a generic planning
    declaration (for example a producer-semantic configuration invariant
    violation). The framework does not interpret producer error types; it only
    translates the boundary failure into a controlled planning error so the
    CLI boundary can map it without knowing any producer class. The original
    producer exception is preserved as this error's cause for diagnostics.
    """


class _SubstrateDefinition(Protocol):
    """Structural shape of a registered substrate definition the planner projects.

    The generic discovery contract (:class:`DiscoverableDefinition`) exposes
    only ``ref`` and ``kind``. For planning, a substrate definition must also
    carry its authoritative normalized output contract. The planner reads it
    structurally from the exact registered object (the registry preserves
    identity); it does not maintain a parallel metadata map.
    """

    ref: ComponentRef
    kind: str
    output_contract: str


def plan_substrate(
    registry: ComponentRegistry,
    target: str | ComponentRef,
    document: LoadedConfiguration,
    *,
    resource_resolver: ResourceResolver,
) -> ExecutionPlan:
    """Plan one substrate build from a registered definition and a loaded document.

    ``registry`` supplies the authoritative registered definition and its
    registered planning capability. ``document`` is the generic loaded
    configuration (Capability 4) passed opaquely to the producer capability. The
    producer capability resolves it (Capability 5) and returns a generic
    :class:`~ehp_sn.planning.capability.PlanningDeclaration`; this function then
    binds the declared resource requirements via ``resource_resolver`` and
    returns an immutable :class:`ExecutionPlan`.

    The expected output contract and selected target reference are derived from
    the registered definition (a single authority); variable scientific inputs
    come from the resolved configuration via the producer declaration.

    Raises :class:`NotASubstrateError` when ``target`` is registered but is not
    a substrate, :class:`MissingPlanningCapabilityError` when the target has no
    registered planning capability, :class:`ProducerResolutionError` when the
    registered producer fails to resolve the document into a declaration, and
    :class:`PlanningError` propagation from resource resolution.

    This function performs no producer execution and no artifact mutation.
    """
    ref = target if isinstance(target, ComponentRef) else ComponentRef.parse(target)
    definition = registry.resolve(ref)

    if definition.kind != _SUBSTRATE_KIND:
        raise NotASubstrateError(
            f"planning requires a substrate target, got component kind {definition.kind!r} "
            f"for reference {ref.canonical!r}"
        )

    capability = registry.capability(ref)
    if capability is None:
        raise MissingPlanningCapabilityError(
            f"no planning capability registered for definition {ref.canonical!r}"
        )
    if not isinstance(capability, SubstratePlanningCapability):
        raise MissingPlanningCapabilityError(
            f"registered capability for {ref.canonical!r} is not a SubstratePlanningCapability"
        )

    try:
        declaration = capability.plan(document)
    except PlanningError:
        raise
    except Exception as exc:
        raise ProducerResolutionError(
            f"producer planning capability for {ref.canonical!r} failed to "
            "resolve the document into a planning declaration"
        ) from exc

    resources: tuple[ResolvedResource, ...] = tuple(
        resource_resolver.resolve(requirement) for requirement in declaration.resources
    )

    substrate = cast(_SubstrateDefinition, definition)
    return ExecutionPlan(
        target=ref,
        output_contract=substrate.output_contract,
        configuration=declaration.configuration,
        resources=resources,
        identity_inputs=declaration.identity_inputs,
    )


__all__ = [
    "MissingPlanningCapabilityError",
    "NotASubstrateError",
    "PlanningError",
    "ProducerResolutionError",
    "plan_substrate",
]
