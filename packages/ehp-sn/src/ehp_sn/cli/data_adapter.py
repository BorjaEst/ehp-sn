"""Registry-backed adapter that connects ``ehp-sn data`` to the framework.

This module adapts real framework objects (the generic discovery registry and
the generic planning machinery) to the temporary CLI-facing seam declared in
``cli/_data_service.py``.

The two responsibilities are deliberately separated:

* ``cli/_data_service.py`` — defines the CLI-facing seam: the ``DataService``
  protocol, the presentation result containers, and the stable user-facing error
  categories;
* ``cli/data_adapter.py`` — adapts real framework objects to that seam.

:class:`FrameworkDataService` is the *production* backend. ``list``/``show`` are
backed by the effective application registry, and ``plan`` delegates to the
single generic framework planning orchestration (``ehp_sn.planning.plan_substrate``)
— the same machinery the Python API uses — injecting the producer planning
composition, then projects the authoritative immutable framework plan into a
CLI-facing :class:`PlanResult`. ``build``/``validate``/``inspect`` remain
explicitly unimplemented for this capability (they raise
:class:`DataNotImplementedError`, surfaced by the CLI as a controlled failure).

The adapter holds no producer-specific branches, metadata maps, or error
classes. It translates only generic framework failures: unknown/malformed
references, generic configuration-loading failures (access/parse), generic
planning failures (not-a-substrate, missing capability, producer resolution),
and generic resource-resolution failures into the stable CLI error categories.
It never imports a concrete research package (ARCH-001).

The adapter consumes the effective application registry; it does not own or
construct one. It is structurally compatible with the ``DataService`` protocol;
explicit inheritance from a ``Protocol`` is not required.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, cast

from ehp_sn.configuration import (
    ConfigurationAccessError,
    ConfigurationParseError,
    load_configuration,
)
from ehp_sn.discovery import ComponentRegistry
from ehp_sn.discovery.registry import UnknownReferenceError
from ehp_sn.experiments import ComponentRef, InvalidReferenceError
from ehp_sn.planning import (
    ExecutionPlan,
    MissingPlanningCapabilityError,
    NotASubstrateError,
    ProducerResolutionError,
    ResolvedResource,
    ResourceResolutionError,
    ResourceResolver,
    SubstratePlanningComposition,
    plan_substrate,
)
from ehp_sn.planning.resources import ResourceRequirement

from ._data_service import (
    BuildResult,
    ConfigurationInvalidError,
    ConfigurationUnreadableError,
    DataNotImplementedError,
    DataOperationError,
    InspectResult,
    ListedSubstrate,
    PlanResult,
    ShowResult,
    UnknownSubstrateError,
    ValidateResult,
)

#: The component kind this adapter's operations accept.
_SUBSTRATE_KIND = "substrate"


class _RegisteredSubstrate(Protocol):
    """Structural shape of a registered substrate definition the adapter projects.

    The generic discovery contract (``DiscoverableDefinition``) exposes only
    ``ref`` and ``kind``. For ``list``/``show`` a substrate definition must also
    carry its authoritative description and normalized output contract. The
    adapter reads those structurally from the exact registered object (the
    registry preserves identity); it does not maintain a parallel metadata map.
    """

    ref: ComponentRef
    kind: str
    description: str
    output_contract: str


def _project_listed_substrate(definition: _RegisteredSubstrate) -> ListedSubstrate:
    """Project a registered substrate definition into a ``data list`` row."""
    return ListedSubstrate(
        ref=definition.ref.canonical,
        family=definition.ref.name,
        output=definition.output_contract,
    )


def _project_show_result(definition: _RegisteredSubstrate) -> ShowResult:
    """Project a registered substrate definition into a ``data show`` result."""
    return ShowResult(
        ref=definition.ref.canonical,
        description=definition.description,
    )


class _DeclaredResourceResolver:
    """Minimal generic resource resolver: bind a requirement's exact declared ref.

    This is the smallest generic binder that satisfies the framework
    resource-resolution boundary for the current planning capability: a
    requirement that declares an exact logical reference (for example an
    upstream source) binds to it; a *required* requirement with no declared
    reference cannot be bound without a dedicated resource subsystem (a later
    capability) and fails cleanly with :class:`ResourceResolutionError`. It
    has no family logic and is not producer specific.
    """

    def resolve(self, requirement: ResourceRequirement) -> ResolvedResource:
        if requirement.definition_resource_ref is None:
            raise ResourceResolutionError(
                f"no exact resource reference for requirement {requirement.ref!r}"
            )
        return ResolvedResource(
            requirement_ref=requirement.ref,
            resource_ref=requirement.definition_resource_ref,
            resolution_source="definition",
        )


def _project_plan(plan: ExecutionPlan) -> PlanResult:
    """Project the authoritative immutable framework plan into a CLI ``plan`` result.

    This is a lossy presentation projection (never the authoritative plan). It
    selects only stable, useful information the authoritative plan genuinely
    supports — the selected target, the expected output contract, the bound
    resource records, and the canonical identity-bearing inputs — and discards
    everything else. It never serializes the opaque producer configuration.
    """
    return PlanResult(
        target=plan.target.canonical,
        output_contract=plan.output_contract,
        resources=plan.resources,
        identity=plan.identity_inputs,
    )


class FrameworkDataService:
    """The registry-backed production backend for the ``ehp-sn data`` CLI group.

    ``list`` enumerates registered substrate definitions from the injected
    registry; ``show`` resolves one authoritative definition and projects it;
    ``plan`` delegates to the single generic framework planning orchestration
    and projects the authoritative immutable plan into a CLI-facing
    :class:`PlanResult`. The remaining lifecycle operations
    (``build``/``validate``/``inspect``) are explicitly not implemented yet.
    """

    def __init__(
        self,
        registry: ComponentRegistry,
        *,
        planning_composition: SubstratePlanningComposition,
        resource_resolver: ResourceResolver | None = None,
    ) -> None:
        self._registry = registry
        self._planning_composition = planning_composition
        self._resource_resolver = resource_resolver or _DeclaredResourceResolver()

    def _resolve_substrate(self, target: str) -> _RegisteredSubstrate:
        """Resolve ``target`` and ensure it denotes a substrate.

        Translates generic framework failures (unknown reference, malformed
        reference) into the CLI-facing :class:`UnknownSubstrateError`, and
        enforces the CLI's operation-specific constraint that the target denote
        a substrate — a generic registry capability, not a new discovery
        primitive. The generic registry never raises a CLI category.
        """
        try:
            definition = self._registry.resolve(target)
        except (UnknownReferenceError, InvalidReferenceError) as exc:
            raise UnknownSubstrateError(f"unknown substrate: {target}") from exc
        if definition.kind != _SUBSTRATE_KIND:
            raise UnknownSubstrateError(f"reference {target} does not denote a substrate")
        return cast("_RegisteredSubstrate", definition)

    def list(self) -> Sequence[ListedSubstrate]:
        """List the registered substrate definitions, in discovery order."""
        definitions = self._registry.iter(kind=_SUBSTRATE_KIND)
        return tuple(
            _project_listed_substrate(cast("_RegisteredSubstrate", definition))
            for definition in definitions
        )

    def show(self, target: str) -> ShowResult:
        """Describe one registered substrate definition, resolved via the registry."""
        definition = self._resolve_substrate(target)
        return _project_show_result(definition)

    def plan(self, target: str, config: str | None) -> PlanResult:
        """Resolve and project a substrate build plan without writing any data.

        Delegates the complete resolution path to the single generic framework
        planning orchestration (``ehp_sn.planning.plan_substrate``), which
        resolves the registered substrate and its planning capability, loads
        the supplied configuration via the generic framework loader, and
        produces the authoritative immutable framework plan. This method does
        not reconstruct the planning pipeline; it only wires configuration
        loading, delegates, and projects the returned plan.

        ``config`` is required: an explicit reusable profile must be supplied.
        A ``None`` configuration is rejected as invalid.

        Performs no producer execution and no artifact mutation.
        """
        if config is None:
            raise ConfigurationInvalidError(
                "data plan requires an explicit --config profile for the target"
            )

        try:
            document = load_configuration(config)
        except ConfigurationAccessError as exc:
            raise ConfigurationUnreadableError(str(exc)) from exc
        except ConfigurationParseError as exc:
            raise ConfigurationInvalidError(str(exc)) from exc

        try:
            plan = plan_substrate(
                self._registry,
                self._planning_composition,
                target,
                document,
                resource_resolver=self._resource_resolver,
            )
        except (UnknownReferenceError, InvalidReferenceError) as exc:
            raise UnknownSubstrateError(f"unknown substrate: {target}") from exc
        except (NotASubstrateError, MissingPlanningCapabilityError) as exc:
            raise UnknownSubstrateError(str(exc)) from exc
        except ResourceResolutionError as exc:
            raise DataOperationError(str(exc)) from exc
        except ProducerResolutionError as exc:
            raise ConfigurationInvalidError(str(exc)) from exc

        return _project_plan(plan)

    def build(self, target: str, config: str | None) -> BuildResult:
        raise DataNotImplementedError(
            f"data build is not yet implemented by the framework backend (target: {target})."
        )

    def validate(self, artifact: str, level: str) -> ValidateResult:
        raise DataNotImplementedError(
            f"data validate is not yet implemented by the framework backend (artifact: {artifact})."
        )

    def inspect(self, artifact: str, samples: int) -> InspectResult:
        raise DataNotImplementedError(
            f"data inspect is not yet implemented by the framework backend (artifact: {artifact})."
        )
