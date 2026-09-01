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
``list``/``show`` are backed by the effective application registry; ``plan``
delegates to the single generic framework planning orchestration
(``ehp_sn.planning.plan_substrate``) — the same machinery the Python API uses —
injecting the producer planning composition, then projects the authoritative
immutable framework plan into a CLI-facing :class:`PlanResult`; ``build``
delegates to the generic build lifecycle (``ehp_sn.artifacts.build_substrate``)
and projects the committed/reused outcome; ``inspect`` resolves a committed
artifact through the generic durable artifact machinery and projects the exact
logical record selected by ``record_id``; ``validate`` resolves a committed
artifact and checks every record against its declared shared logical schema
through the single framework-owned shared-contract validator.

The adapter holds no producer-specific branches, metadata maps, or error
classes. It translates only generic framework failures: unknown/malformed
references, generic configuration-loading failures (access/parse), generic
planning failures (not-a-substrate, missing capability, producer resolution),
generic resource-resolution failures, and generic artifact/record-resolution
failures into the stable CLI error categories. It never imports a concrete
research package (ARCH-001).

The adapter consumes the effective application registry; it does not own or
construct one.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

from ehp_sn.artifacts import (
    BuildOutcome,
    ConflictBuildError,
    InvalidExistingStateBuildError,
    ReleaseNotConfiguredBuildError,
    StoreError,
    build_substrate,
    load_release,
    resolve_release,
)
from ehp_sn.artifacts.manifest import ManifestParseError
from ehp_sn.configuration import (
    ConfigurationAccessError,
    ConfigurationParseError,
    load_configuration,
)
from ehp_sn.discovery import ComponentRegistry
from ehp_sn.discovery.registry import UnknownReferenceError
from ehp_sn.execution import (
    ExecutionError,
    LogicalRecord,
    SubstrateExecutionComposition,
)
from ehp_sn.experiments import ComponentRef, InvalidReferenceError
from ehp_sn.planning import (
    ExecutionPlan,
    MissingPlanningCapabilityError,
    NotASubstrateError,
    ProducerResolutionError,
    ReleaseCoordinateResolutionError,
    ResolvedResource,
    ResourceResolutionError,
    ResourceResolver,
    SubstratePlanningComposition,
    plan_substrate,
)
from ehp_sn.planning.resources import ResourceRequirement

#: The component kind this adapter's operations accept.
_SUBSTRATE_KIND = "substrate"

#: Default local artifact root (the "interim-data root") for committed substrate
#: releases: ``<root>/<family>/<variant>/v<N>/``. The monorepo convention places
#: committed substrates under ``data/interim/``.
_DEFAULT_ARTIFACT_ROOT = Path("data/interim")

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


class UnknownArtifactError(DataCliError):
    """The requested artifact is absent or cannot be read as a committed release.

    Raised when the supplied artifact (physically or by ``artifact:`` reference)
    does not resolve to a committed substrate release.
    """

    exit_code = 4  # referenced input not found or unreadable
    category = "unknown_artifact"


class ArtifactInvalidError(DataCliError):
    """The requested artifact exists but is not a valid committed release.

    A present but uncommitted, corrupt, or structurally incomplete release (for
    example a missing or unparseable manifest, or a digest-inconsistent
    resource) surfaces as this controlled category rather than a raw filesystem
    or parse exception.
    """

    exit_code = 4  # referenced input not found or unreadable
    category = "artifact_invalid"


class RecordNotFoundError(DataCliError):
    """The requested ``record_id`` does not exist in the artifact.

    A valid committed artifact that contains no record with the requested
    record identifier surfaces as this controlled category, never a raw index
    error.
    """

    exit_code = 4  # referenced input not found
    category = "record_not_found"


class DataNotConformingError(DataCliError):
    """A committed artifact contains a record non-conforming to its declared contract.

    A present, readable committed artifact whose logical records do **not**
    conform to their declared shared logical schema surfaces as this controlled
    category (exit 3, invalid configuration or specification). No record is
    silently repaired; conformance failure is explicit (``docs/invariants.md``
    ARCH-014). This is distinct from an unreadable/corrupt artifact
    (:class:`ArtifactInvalidError`), which concerns physical validity.
    """

    exit_code = 3  # invalid configuration or specification
    category = "record_not_conforming"


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


@dataclass(frozen=True)
class BuildResult:
    """A ``data build`` projection of the framework build outcome.

    This is a presentational, deterministic projection of the framework-domain
    :class:`~ehp_sn.artifacts.BuildOutcome`. It is **not** the framework result
    and carries no exit code.

    It exposes the stable lifecycle outcome (``committed`` or ``reused``), the
    committed target, the output contract, the committed artifact's build-input
    identity and artifact fingerprint, and — for a real new or reused
    publication — the canonical artifact reference and the local physical
    release coordinate (the CLI contract exposes the local coordinate for the
    monorepo persistence binding). The framework result remains authoritative;
    this view is only what the CLI renders.
    """

    action: str
    target: str
    output_contract: str
    build_input_identity: str
    artifact_fingerprint: str
    artifact_ref: str | None = None
    location: str | None = None


@dataclass(frozen=True)
class InspectResult:
    """A ``data inspect`` projection of one exact logical record.

    This is a presentational, deterministic projection of one framework
    :class:`~ehp_sn.execution.LogicalRecord` from a committed
    :class:`~ehp_sn.artifacts.SubstrateArtifact`. It is **not** the framework
    value object.

    It carries enough information for generic textual inspection:

    * ``artifact_ref`` — the committed artifact's canonical ``artifact:``
      reference (its identity/reference);
    * ``record_id`` — the exact framework record identifier;
    * ``schema_ref`` — the schema the record conforms to;
    * ``content`` — the opaque generic record content (never interpreted by a
      producer-specific or contract-specific branch).

    No raster/producer/contract-specific presentation is introduced here
    (``docs/invariants.md`` ARCH-014); presentation is a CLI concern.
    """

    artifact_ref: str
    record_id: str
    schema_ref: str
    content: object


@dataclass(frozen=True)
class RecordConformanceView:
    """CLI-facing value of one non-conforming logical record.

    ``record_id`` addresses the exact record; ``schema_ref`` is its declared
    logical schema; ``invariant`` and ``message`` identify the violated
    ``*-REC-*`` invariant and the observed-vs-expected detail.
    """

    record_id: str
    schema_ref: str
    invariant: str
    message: str


@dataclass(frozen=True)
class ValidateResult:
    """A ``data validate`` projection of shared-contract conformance.

    This is a presentational, deterministic projection of validating every
    logical record of a committed artifact against its declared shared logical
    schema (``docs/invariants.md`` ARCH-014). It is **not** the framework
    validation authority; it reports observable conformance.

    It carries the committed artifact reference, the total record count, the
    count of conforming records, and the exact list of non-conforming records
    (as :class:`RecordConformanceView` values) — or an empty list when every
    record conforms. No sampling or RNG is performed; the check is total and
    deterministic over the committed records.
    """

    artifact_ref: str
    total_records: int
    conforming_records: int
    non_conforming: tuple[RecordConformanceView, ...]


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
            IdentityInputView(name=input_.name, value=input_.value)
            for input_ in plan.identity_inputs
        ),
    )


class FrameworkDataAdapter:
    """The registry-backed production adapter for the ``ehp-sn data`` CLI group.

    ``list`` enumerates registered substrate definitions from the injected
    registry; ``show`` resolves one authoritative definition and projects it;
    ``plan`` delegates to the single generic framework planning orchestration
    (``ehp_sn.planning.plan_substrate``) and projects the authoritative
    immutable plan into a CLI-facing :class:`PlanResult`; ``build`` delegates to
    the single generic framework build orchestration
    (``ehp_sn.artifacts.build_substrate``) and projects the framework build
    outcome into a CLI-facing :class:`BuildResult`; ``inspect`` resolves a
    committed substrate artifact through the existing durable artifact machinery
    (``ehp_sn.artifacts.load_release`` / ``resolve_release``) and projects the
    exact logical record selected by ``record_id`` into a generic
    :class:`InspectResult`.

    The build and inspect paths intentionally do little more than invoke the
    generic lifecycles, translate controlled framework errors, and project the
    result: they do not load TOML except through the established generic path,
    do not inspect producer configuration, do not select execution operations,
    do not allocate releases, do not compute fingerprints, and do not publish or
    understand logical-resource formats — those are all framework
    responsibilities.

    ``validate`` is deliberately absent: it remains unsupported until the
    corresponding framework capability exists, so no placeholder method pretends
    it does.
    """

    def __init__(
        self,
        registry: ComponentRegistry,
        *,
        planning_composition: SubstratePlanningComposition,
        execution_composition: SubstrateExecutionComposition,
        resource_resolver: ResourceResolver | None = None,
        root: Path | None = None,
    ) -> None:
        self._registry = registry
        self._planning_composition = planning_composition
        self._execution_composition = execution_composition
        self._resource_resolver = resource_resolver or _DeclaredResourceResolver()
        # The artifact root under which committed substrate releases are placed
        # (the "interim-data root": `data/interim/<family>/<variant>/v<N>/`).
        self._root = root or _DEFAULT_ARTIFACT_ROOT

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
            raise UnknownSubstrateError(
                f"reference {target} does not denote a substrate"
            )
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

    def _resolve_artifact(self, artifact: str):
        """Resolve a user-supplied ``ARTIFACT`` into a committed substrate artifact.

        ``artifact`` is either a physical path to a committed release directory
        or a canonical ``artifact:<name>/v<N>`` reference. It reuses the
        existing durable artifact-resolution machinery
        (``ehp_sn.artifacts.load_release`` / ``resolve_release``); it does not
        build a parallel artifact resolver (``docs/invariants.md`` ARCH-014).

        Controlled framework failures (an absent artifact, a corrupt/uncommitted
        release, a malformed reference) are translated into the CLI-facing
        categories, never leaked as raw filesystem or parse exceptions.
        """
        from ehp_sn.planning import ReleaseCoordinate

        reference = artifact.strip()
        if reference.lower().startswith("artifact:"):
            try:
                parsed = ComponentRef.parse(reference)
            except InvalidReferenceError as exc:
                raise UnknownArtifactError(
                    f"malformed artifact reference: {artifact}"
                ) from exc
            if parsed.kind != "artifact":
                raise UnknownArtifactError(
                    f"reference {artifact} does not denote an artifact"
                )
            try:
                family, _, variant = parsed.name.partition("/")
                if not variant:
                    raise UnknownArtifactError(
                        f"artifact reference {artifact} must name <family>/<variant>"
                    )
                coordinate = ReleaseCoordinate(
                    family=family, variant=variant, release=parsed.version
                )
                return resolve_release(self._root, coordinate)
            except (StoreError, ManifestParseError) as exc:
                raise UnknownArtifactError(str(exc)) from exc

        location = Path(reference)
        try:
            return load_release(location)
        except (StoreError, ManifestParseError) as exc:
            raise UnknownArtifactError(str(exc)) from exc

    def inspect(self, artifact: str, record_id: str) -> InspectResult:
        """Inspect exactly one logical record of a committed substrate artifact.

        The deterministic bootstrap path: a user-supplied ``ARTIFACT`` (path or
        ``artifact:`` reference) is resolved to its committed
        :class:`~ehp_sn.artifacts.SubstrateArtifact`, the exact ``record_id`` is
        looked up through the existing record-identity mechanism, and the exact
        :class:`~ehp_sn.execution.LogicalRecord` is projected generically.

        This is a single deterministic lookup: one committed artifact, one
        explicit ``record_id``, one exact logical record. No implicit ordering,
        RNG, or representative sampling is performed (``docs/invariants.md``
        ARCH-014; Phase 0R P0R-3).

        The projection is generic: no producer-specific or contract-specific
        branch decides how the record is presented.
        """
        committed = self._resolve_artifact(artifact)
        record = committed.record(record_id)
        if record is None:
            raise RecordNotFoundError(
                f"record {record_id!r} not found in committed artifact {committed.artifact_ref}"
            )
        return _project_inspect_result(committed, record)

    def validate(self, artifact: str) -> ValidateResult:
        """Validate every committed logical record against its declared shared schema.

        The deterministic conformance path: a user-supplied ``ARTIFACT`` (path
        or ``artifact:`` reference) is resolved to its committed
        :class:`~ehp_sn.artifacts.SubstrateArtifact`, and every logical record's
        opaque ``content`` is validated against its declared shared logical
        schema through the single framework-owned shared-contract validation
        authority (``ehp_sn.contracts.validation``). No record is silently
        repaired and no producer-specific or contract-specific branch interprets
        content (``docs/invariants.md`` ARCH-014).

        The check is total and deterministic: every committed record is
        validated once, in index/registration order, with no sampling or RNG.
        A record whose declared schema is not a recognized shared contract is
        reported as non-conforming (unknown schema), never silently skipped.

        Returns a :class:`ValidateResult` describing artifact reference, total
        and conforming counts, and the exact non-conforming records. Raises
        :class:`DataNotConformingError` when one or more records are
        non-conforming, and :class:`UnknownArtifactError` /
        :class:`ArtifactInvalidError` for resolution/parse failures resolved via
        the shared :meth:`_resolve_artifact` path.
        """
        committed = self._resolve_artifact(artifact)
        non_conforming: list[RecordConformanceView] = []
        for record in committed.records:
            failure = _validate_record_content(record.schema_ref, record.content)
            if failure is not None:
                non_conforming.append(
                    RecordConformanceView(
                        record_id=record.record_id,
                        schema_ref=record.schema_ref,
                        invariant=failure.invariant,
                        message=failure.message,
                    )
                )
        total = len(committed.records)
        if non_conforming:
            raise DataNotConformingError(
                f"{len(non_conforming)} of {total} records are non-conforming to "
                "their declared shared contract (first: "
                f"{non_conforming[0].schema_ref} {non_conforming[0].invariant})"
            )
        return ValidateResult(
            artifact_ref=committed.artifact_ref,
            total_records=total,
            conforming_records=total,
            non_conforming=(),
        )

    def plan(
        self, target: str, config: str | None, release: int | None = None
    ) -> PlanResult:
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

        ``release`` selects the intended publication coordinate (``--release``).
        It is the highest authority for the coordinate and never participates in
        scientific build identity. A ``release`` value declared in the effective
        configuration is a temporary compatibility fallback.

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
                release=release,
            )
        except (UnknownReferenceError, InvalidReferenceError) as exc:
            raise UnknownSubstrateError(f"unknown substrate: {target}") from exc
        except (NotASubstrateError, MissingPlanningCapabilityError) as exc:
            raise UnknownSubstrateError(str(exc)) from exc
        except ResourceResolutionError as exc:
            raise DataOperationError(str(exc)) from exc
        except ProducerResolutionError as exc:
            raise ConfigurationInvalidError(str(exc)) from exc
        except ReleaseCoordinateResolutionError as exc:
            raise ConfigurationInvalidError(str(exc)) from exc

        return _project_plan(plan)

    def build(
        self, target: str, config: str | None, release: int | None = None
    ) -> BuildResult:
        """Run one generic substrate build and project the framework outcome.

        Delegates the complete lifecycle to the single generic framework build
        orchestration (``ehp_sn.artifacts.build_substrate``), which loads and
        plans exactly once, executes the exact plan, assembles and commits the
        artifact, and returns a framework-domain :class:`BuildOutcome` (``None``
        for the conflict/producer-translated case → a controlled CLI error).

        ``config`` is required: an explicit reusable profile must be supplied. A
        ``None`` configuration is rejected as invalid.

        ``release`` selects the intended publication coordinate (``--release``),
        passed through to the build exactly once; a build must not re-resolve a
        different release than the one selected here. It is the highest
        authority for the coordinate and never participates in scientific build
        identity.

        Controlled framework execution failures (:class:`ExecutionError`,
        including a missing execution capability) are translated here into a
        controlled :class:`DataOperationError` (exit 6) with no traceback, so a
        target with no execution capability fails cleanly instead of leaking the
        framework hierarchy.

        This method does not re-implement any lifecycle stage; it only wires the
        injected compositions, delegates, translates controlled framework
        errors, and projects the result.
        """
        if config is None:
            raise ConfigurationInvalidError(
                "data build requires an explicit --config profile for the target"
            )

        try:
            outcome: BuildOutcome = build_substrate(
                registry=self._registry,
                planning_composition=self._planning_composition,
                execution_composition=self._execution_composition,
                target=target,
                config=config,
                resource_resolver=self._resource_resolver,
                root=self._root,
                release=release,
            )
        except ReleaseNotConfiguredBuildError as exc:
            raise DataOperationError(str(exc)) from exc
        except ConflictBuildError as exc:
            raise DataOperationError(str(exc)) from exc
        except InvalidExistingStateBuildError as exc:
            raise DataOperationError(str(exc)) from exc
        except StoreError as exc:
            raise DataOperationError(str(exc)) from exc
        except ExecutionError as exc:
            raise DataOperationError(str(exc)) from exc
        except ConfigurationAccessError as exc:
            raise ConfigurationUnreadableError(str(exc)) from exc
        except ConfigurationParseError as exc:
            raise ConfigurationInvalidError(str(exc)) from exc
        except (UnknownReferenceError, InvalidReferenceError) as exc:
            raise UnknownSubstrateError(f"unknown substrate: {target}") from exc
        except (NotASubstrateError, MissingPlanningCapabilityError) as exc:
            raise UnknownSubstrateError(str(exc)) from exc
        except (ProducerResolutionError, ResourceResolutionError) as exc:
            raise ConfigurationInvalidError(str(exc)) from exc
        except ReleaseCoordinateResolutionError as exc:
            raise ConfigurationInvalidError(str(exc)) from exc

        return _project_build_result(outcome)


def _project_inspect_result(committed: object, record: LogicalRecord) -> InspectResult:
    """Project one exact logical record into a generic ``data inspect`` result.

    A lossy presentation projection (never the framework value object). Selects
    the committed artifact's canonical reference, the exact record identifier,
    the record's schema reference, and the opaque generic content. It performs
    no producer-specific or contract-specific branching.
    """
    from ehp_sn.artifacts import SubstrateArtifact

    committed_typed = cast("SubstrateArtifact", committed)
    return InspectResult(
        artifact_ref=committed_typed.artifact_ref,
        record_id=record.record_id,
        schema_ref=record.schema_ref,
        content=record.content,
    )


def _validate_record_content(schema_ref: str, content: object):
    """Validate one logical record's content against its declared schema.

    Dispatches the opaque ``content`` to the single framework-owned
    shared-contract validation authority (``ehp_sn.contracts.validation``) keyed
    by the record's declared ``schema_ref``. Returns ``None`` when the record
    conforms, or a :class:`~ehp_sn.contracts.validation.ContractValidationError`
    carrying the violated invariant and message when it does not.

    A declared schema that is not a recognized shared contract is reported as
    non-conforming (unknown schema) rather than silently skipped, so a record
    never escapes validation. No producer-specific branch decides the outcome.
    """
    from ehp_sn.contracts.validation import (
        ContractValidationError,
        validate_categorical_field,
        validate_raster_topology,
        validate_simple_digraph,
    )

    _VALIDATORS = {
        "simple-digraph/v1": validate_simple_digraph,
        "raster-topology/v1": validate_raster_topology,
        "categorical-field/v1": validate_categorical_field,
    }
    validator = _VALIDATORS.get(schema_ref)
    if validator is None:
        return ContractValidationError(
            schema_ref,
            "schema",
            f"no shared contract validator registered for declared schema {schema_ref!r}",
        )
    if not isinstance(content, dict):
        return ContractValidationError(
            schema_ref,
            "decode",
            f"declared logical instance must be a mapping, got {type(content).__name__}",
        )
    try:
        validator(content)
    except ContractValidationError as exc:
        return exc
    return None


def _project_build_result(outcome: BuildOutcome) -> BuildResult:
    """Project the framework build outcome into a CLI ``build`` result.

    A lossy presentation projection (never the framework result). Selects the
    lifecycle outcome, target, output contract, the committed artifact's
    build-input identity and artifact fingerprint, and — for a real committed or
    reused release — the canonical artifact reference and the local release
    coordinate.
    """
    artifact = outcome.artifact
    return BuildResult(
        action=outcome.action,
        target=artifact.component_ref,
        output_contract=artifact.output_contract,
        build_input_identity=artifact.build_input_identity,
        artifact_fingerprint=artifact.artifact_fingerprint,
        artifact_ref=artifact.artifact_ref,
        location=str(artifact.location),
    )
