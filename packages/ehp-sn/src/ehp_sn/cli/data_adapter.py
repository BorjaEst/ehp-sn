"""Registry-backed adapter that connects ``ehp-sn data`` to the framework.

This module is the production CLI boundary for the ``ehp-sn data`` command
group. It holds three responsibilities:

* :class:`FrameworkDataAdapter` — adapts real framework objects (the generic
  discovery registry and the generic planning machinery) to the CLI;
* the CLI-facing presentation DTOs the CLI renders to text/JSON
  (``ListedSubstrate``, ``ShowResult``, ``PlanResult`` and their value views);
* the stable CLI-facing error categories the CLI maps to exit codes
  (:class:`DataCliError` and subclasses).

These live here because there is no separate generic CLI error module: the
error categories are data-CLI-specific and are exercised only through this
adapter boundary.

:class:`FrameworkDataAdapter` adapts real framework objects to the CLI.
``list``/``show`` are backed by the effective application registry, and
``plan`` delegates to the single generic framework planning orchestration
(``ehp_sn.planning.plan_substrate``) — the same machinery the Python API uses —
injecting the producer planning composition, then projects the authoritative
immutable framework plan into a CLI-facing :class:`PlanResult`. The future
execution/artifact lifecycle (``build``/``validate``/``inspect``) is not part
of this adapter's surface; those commands are reported by the CLI itself as
unsupported until real framework capabilities exist.

The adapter holds no producer-specific branches, metadata maps, or error
classes. It translates only generic framework failures: unknown/malformed
references, generic configuration-loading failures (access/parse), generic
planning failures (not-a-substrate, missing capability, producer resolution),
and generic resource-resolution failures into the stable CLI error categories.
It never imports a concrete research package (ARCH-001).

The adapter consumes the effective application registry; it does not own or
construct one.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Protocol, cast

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

#: The component kind this adapter's operations accept.
_SUBSTRATE_KIND = "substrate"

# ---------------------------------------------------------------------------
# Stable user-facing error categories
#
# These are the categories the CLI treats as controlled failures. The mapping
# to process exit codes follows the authoritative table in
# ``docs/docs/interfaces/cli/index.md`` § "Exit codes".
# ---------------------------------------------------------------------------


class DataCliError(Exception):
    """Base class for controlled, user-facing data CLI errors.

    A ``DataCliError`` is not an internal bug: it is an expected condition the
    CLI surfaces as a concise message and a stable exit code, never as a
    normal-user traceback. It is a CLI-facing category, not a framework
    service-domain exception.
    """

    #: Process exit code associated with this category.
    exit_code: int
    #: Stable machine-readable category name.
    category: str

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class UnknownSubstrateError(DataCliError):
    """The requested substrate target is not known to the registry/backing machinery."""

    exit_code = 4  # referenced input not found
    category = "unknown_substrate"


class ConfigurationUnreadableError(DataCliError):
    """The supplied configuration file is absent or cannot be read."""

    exit_code = 4  # referenced file absent or unreadable
    category = "configuration_unreadable"


class ConfigurationInvalidError(DataCliError):
    """The supplied configuration file is present but invalid."""

    exit_code = 3  # invalid configuration or specification
    category = "configuration_invalid"


class DataOperationError(DataCliError):
    """A generic framework planning/resolution failure the current slice maps to a CLI category.

    Kept only while current planning genuinely maps an implemented generic
    planning failure (a resource-resolution failure) to this category.
    """

    exit_code = 6  # execution failure
    category = "operation_failed"


class DataNotImplementedError(DataCliError):
    """A command the CLI exposes is not yet implemented by a real capability.

    This is the controlled translation of a CLI command that is part of the
    established command surface but intentionally unsupported until the
    corresponding framework capability lands, so the CLI does not leak a
    traceback to a normal user.
    """

    exit_code = 1  # unexpected internal or operational failure
    category = "operation_not_implemented"


# ---------------------------------------------------------------------------
# CLI presentation DTOs
#
# These are explicit CLI-facing projections, deliberately distinct from the
# internal framework value objects. The CLI renders these to text/JSON; it must
# not accidentally expose internal framework representation as public CLI API.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ListedSubstrate:
    """One row of a ``data list`` result."""

    ref: str
    family: str
    output: str


@dataclass(frozen=True)
class ShowResult:
    """A ``data show`` description of one substrate."""

    ref: str
    description: str


@dataclass(frozen=True)
class ResolvedResourceView:
    """CLI-facing value of one bound logical resource (presentation value)."""

    requirement_ref: str
    resource_ref: str
    resolution_source: str


@dataclass(frozen=True)
class IdentityInputView:
    """CLI-facing value of one identity-bearing scientific input (presentation value)."""

    name: str
    value: Any


@dataclass(frozen=True)
class PlanResult:
    """A ``data plan`` projection of the authoritative framework execution plan.

    This is a presentational, deterministic projection of the immutable
    framework :class:`~ehp_sn.planning.ExecutionPlan`. It is **not** itself the
    authoritative plan and is never used to drive build execution: build will
    consume the framework plan, while this projection is only what the CLI
    renders.

    It carries only stable, useful information that the authoritative plan
    genuinely supports:

    * ``target`` — the canonical reference of the planned substrate;
    * ``output_contract`` — the expected normalized output schema reference,
      derived from the registered definition (single authority);
    * ``resources`` — the exact bound logical resource records the build would
      rely on (empty when the producer declares none), projected as
      :class:`ResolvedResourceView` values;
    * ``identity`` — the canonical, ordered producer-declared identity-bearing
      scientific inputs that contribute to build identity, projected as
      :class:`IdentityInputView` values.

    The projection never exposes internal framework value objects
    (:class:`~ehp_sn.planning.ResolvedResource` /
    :class:`~ehp_sn.planning.IdentityInput`). No artifact destination,
    conflict/reuse status, or identity hash is included because the framework
    plan available to this capability does not establish those yet; fields are
    added only when the authoritative plan supports them.
    """

    target: str
    output_contract: str
    resources: tuple[ResolvedResourceView, ...]
    identity: tuple[IdentityInputView, ...]


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
        resources=tuple(
            ResolvedResourceView(
                requirement_ref=resource.requirement_ref,
                resource_ref=resource.resource_ref,
                resolution_source=resource.resolution_source,
            )
            for resource in plan.resources
        ),
        identity=tuple(
            IdentityInputView(name=input_.name, value=input_.value) for input_ in plan.identity_inputs
        ),
    )


class FrameworkDataAdapter:
    """The registry-backed production adapter for the ``ehp-sn data`` CLI group.

    ``list`` enumerates registered substrate definitions from the injected
    registry; ``show`` resolves one authoritative definition and projects it;
    ``plan`` delegates to the single generic framework planning orchestration
    and projects the authoritative immutable plan into a CLI-facing
    :class:`PlanResult`.

    The future execution/artifact lifecycle (``build``/``validate``/``inspect``)
    is deliberately **absent** from this adapter: there is no concrete framework
    capability for it yet, so no placeholder method pretends it exists.
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
