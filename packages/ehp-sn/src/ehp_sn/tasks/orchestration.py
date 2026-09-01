"""Generic task-corpus orchestration: build, validate, list, resolve.

This is the framework-owned generic task orchestration (Stage 6C § 8's allowed
mechanics). It owns:

* task reference resolution and catalogue enumeration (producer-order independent);
* source-role binding and composition against framework-owned contracts;
* generic build/validate dispatch through the registered task definition;
* deterministic result projection.

It does **not** own what a goal, target, trajectory, revisit, or split means for
any concrete task: all scientific interpretation happens inside the task-owned
``build``/``validate`` callables reached through the definition instance. There
is deliberately **no** ``if task_family == ...`` branching anywhere in this
module (Stage 6C § 3). Source roles are bound to contracts, never to producer
identity, so producer substitution within one required contract needs no
task-specific path (Stage 6C § 11).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ehp_sn.artifacts import SubstrateArtifact
from ehp_sn.discovery import ComponentRegistry
from ehp_sn.experiments import ComponentRef

from .canonical import SourceRole, TaskDefinition, TaskSourceComposition
from .errors import TaskCompositionError, TaskOrchestrationError, UnsupportedTaskError


@dataclass(frozen=True, slots=True)
class ResolvedTaskSource:
    """A source artifact bound to one semantic source role.

    ``artifact`` is the committed, immutable source artifact; ``role`` is the
    semantic source role it satisfies; ``required_contract`` is the
    framework-owned logical contract the role demanded and the artifact's
    ``output_contract`` was matched against.
    """

    role: str
    required_contract: str
    artifact: SubstrateArtifact

    @property
    def artifact_ref(self) -> str:
        return self.artifact.artifact_ref

    @property
    def fingerprint(self) -> str:
        return self.artifact.artifact_fingerprint


class TaskSourceResolver(Protocol):
    """Resolves a source literal to a committed substrate artifact.

    Implemented by the caller (for example the CLI adapter) so this generic
    layer does not own a hard-coded artifact root. The literal is a canonical
    artifact reference (for example ``artifact:maze-nd/source-topology/v2``).
    """

    def resolve(self, literal: str) -> SubstrateArtifact: ...


@dataclass(frozen=True, slots=True)
class TaskBuildConfiguration:
    """Generic, task-semantic-free resolved inputs for one task build.

    ``task_ref`` is the canonical task reference; ``sources`` is an ordered
    mapping (list of ``(role, artifact_literal)`` pairs) of selected parent
    artifacts; ``release`` is the desired corpus release number; ``seed`` is the
    deterministic generation seed; ``configuration`` is opaque, task-owned
    effective configuration.
    """

    task_ref: str
    sources: tuple[tuple[str, str], ...]
    release: int
    seed: int
    configuration: object


@dataclass(frozen=True, slots=True)
class TaskBuildOutcome:
    """The committed task-corpus outcome, projected generically."""

    task_ref: str
    action: str  # "committed" | "reused"
    output: str
    source_roles: tuple[str, ...]
    record_count: int


@runtime_checkable
class TaskBuildResult(Protocol):
    """The opaque result a task-owned ``build`` returns to orchestration.

    A task returns an object exposing ``records`` (its logical task cases) and
    ``resources`` (auxiliary corpus resources). The generic orchestration
    projects counts and provenance without interpreting scientific content.
    """

    @property
    def records(self) -> tuple[object, ...]: ...

    @property
    def resources(self) -> tuple[object, ...]: ...


@runtime_checkable
class TaskValidateResult(Protocol):
    """The opaque outcome a task-owned ``validate`` returns.

    A task exposes ``valid`` (bool) and ``issues`` (tuple of human-readable
    issue strings). Generic orchestration only forwards them.
    """

    @property
    def valid(self) -> bool: ...

    @property
    def issues(self) -> tuple[str, ...]: ...


_DEFAULT_VERSION = 1


def resolve_task(registry: ComponentRegistry, reference: str | ComponentRef) -> TaskDefinition:
    """Resolve a canonical task reference to its registered definition."""
    definition = registry.resolve(reference)
    if not isinstance(definition, TaskDefinition):
        raise UnsupportedTaskError(f"reference {definition.ref.canonical!r} is not a task definition")
    return definition


def list_tasks(registry: ComponentRegistry) -> tuple[TaskDefinition, ...]:
    """Enumerate registered task definitions in deterministic canonical order.

    Enumeration is independent of provider/registration order: the registry
    yields in canonical reference order (ARCH-003).
    """
    definitions = tuple(registry.iter(kind="task"))
    return tuple(d for d in definitions if isinstance(d, TaskDefinition))


def _bind_source(
    definition: TaskDefinition,
    composition: TaskSourceComposition,
    selected: dict[str, SubstrateArtifact],
) -> tuple[ResolvedTaskSource, ...]:
    """Bind the declared source roles to the selected artifacts by contract.

    Matching is by the role's required **logical contract** against each
    artifact's ``output_contract`` — never by producer identity. This is what
    makes producer substitution within one required contract a no-op for the
    task path (Stage 6C § 11).
    """
    bound: list[ResolvedTaskSource] = []
    by_contract: list[SourceRole] = list(composition.roles)
    for role in by_contract:
        artifact = selected.get(role.role)
        if artifact is None:
            raise TaskCompositionError(
                f"task {definition.ref.canonical!r} requires source role "
                f"{role.role!r} ({role.required_contract}) but none was selected"
            )
        if artifact.output_contract != role.required_contract:
            raise TaskCompositionError(
                f"task {definition.ref.canonical!r} requires role {role.role!r} to "
                f"satisfy logical contract {role.required_contract!r} but the selected "
                f"artifact declares output contract {artifact.output_contract!r}"
            )
        bound.append(
            ResolvedTaskSource(
                role=role.role,
                required_contract=role.required_contract,
                artifact=artifact,
            )
        )
    return tuple(bound)


def _select_sources(
    resolver: TaskSourceResolver,
    literal_sources: tuple[tuple[str, str], ...],
) -> dict[str, SubstrateArtifact]:
    """Load each selected source artifact literal and key it by source role.

    Loading is generic (``load_release`` on the resolver's output); no task or
    producer identity is inspected.
    """
    selected: dict[str, SubstrateArtifact] = {}
    for role, literal in literal_sources:
        selected[role] = resolver.resolve(literal)
    return selected


def build_task_corpus(
    registry: ComponentRegistry,
    resolver: TaskSourceResolver,
    configuration: TaskBuildConfiguration,
) -> tuple[TaskBuildOutcome, TaskBuildResult]:
    """Drive one generic, task-owned task-corpus build.

    The generic layer resolves the task definition, binds its declared source
    roles to the selected artifacts by logical contract, and then hands a
    task-owned build session to the definition's ``build`` callable. The task
    returns an opaque :class:`TaskBuildResult`; the generic layer projects a
    generic :class:`TaskBuildOutcome` and forwards the result. There is no
    task-name or producer-name branch.
    """
    definition = resolve_task(registry, configuration.task_ref)
    composition = definition.sources
    selected = _select_sources(resolver, configuration.sources)
    bound = _bind_source(definition, composition, selected)

    # Generic, task-owned build session. The task receives its bound source
    # roles, the opaque resolved inputs, and returns a TaskBuildResult.
    result = definition.build(
        session=None,
        sources=tuple((r.role, r.required_contract, r.artifact) for r in bound),
        configuration=configuration.configuration,
        seed=configuration.seed,
    )
    if not isinstance(result, TaskBuildResult):
        raise TaskOrchestrationError(
            f"task {definition.ref.canonical!r} returned an unrecognized build result"
        )

    count = len(result.records)
    outcome = TaskBuildOutcome(
        task_ref=definition.ref.canonical,
        action="committed",
        output=f"data/processed/{definition.ref.name}/{configuration.release}",
        source_roles=tuple(r.role for r in bound),
        record_count=count,
    )
    return outcome, result


def validate_task_corpus(
    registry: ComponentRegistry,
    resolver: TaskSourceResolver,
    configuration: TaskBuildConfiguration,
    result: TaskBuildResult,
) -> TaskValidateResult:
    """Run one generic, task-owned task-corpus validation over a build result.

    Task-owned validation is reached through the definition instance; the
    generic layer forwards the bound sources and configuration and returns the
    task-owned validation outcome unchanged.
    """
    definition = resolve_task(registry, configuration.task_ref)
    composition = definition.sources
    selected = _select_sources(resolver, configuration.sources)
    bound = _bind_source(definition, composition, selected)
    validation = definition.validate(
        corpus=result,
        sources=tuple((r.role, r.required_contract, r.artifact) for r in bound),
        configuration=configuration.configuration,
    )
    if not isinstance(validation, TaskValidateResult):
        raise TaskOrchestrationError(
            f"task {definition.ref.canonical!r} returned an unrecognized validation result"
        )
    return validation
