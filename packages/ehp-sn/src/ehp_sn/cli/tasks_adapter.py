"""Registry-backed adapter for the ``ehp-sn tasks`` command group.

This module is the production CLI boundary for ``ehp-sn tasks``. It adapts the
generic task framework (``ehp_sn.tasks``) and the durable artifact resolver to
the CLI, projecting task definitions into CLI-facing DTOs and mapping generic
task failures to stable CLI error categories.

Like ``data_adapter``, this adapter holds no producer- or task-specific
branches: it enumerates registered task definitions generically and never
inspects a task family's scientific meaning. It never imports ``ehp_research``
(ARCH-001).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ehp_sn.artifacts import StoreError, load_release
from ehp_sn.artifacts.manifest import ManifestParseError
from ehp_sn.discovery import ComponentRegistry
from ehp_sn.discovery.registry import UnknownReferenceError
from ehp_sn.experiments import InvalidReferenceError
from ehp_sn.tasks import UnsupportedTaskError, list_tasks, resolve_task

#: Default local artifact root for committed substrate releases.
_DEFAULT_ARTIFACT_ROOT = Path("data/interim")


class TasksCliError(Exception):
    """Base class for controlled, user-facing ``tasks`` CLI errors."""

    exit_code: int
    category: str

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class UnknownTaskError(TasksCliError):
    """The requested task is not registered in the effective catalogue."""

    exit_code = 4
    category = "unknown_task"


class SourceResolutionError(TasksCliError):
    """A declared source artifact could not be resolved."""

    exit_code = 4
    category = "source_unresolved"


class TaskCompositionCliError(TasksCliError):
    """The task's source-role composition could not be satisfied."""

    exit_code = 3
    category = "task_composition"


@dataclass(frozen=True, slots=True)
class ListedTask:
    """A task-family catalogue row (``tasks list``)."""

    ref: str
    purpose: str
    source_roles: tuple[str, ...]
    contracts: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TaskShowResult:
    """One task-family contract summary (``tasks show``)."""

    ref: str
    purpose: str
    source_roles: tuple[tuple[str, str], ...]
    required_contracts: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TaskPlanResult:
    """A dry-run task build resolution (``tasks plan``)."""

    task_ref: str
    resolved_sources: tuple[tuple[str, str, str], ...]  # role, ref, fingerprint
    release: int
    seed: int
    projected_case_count: int | None


@dataclass(frozen=True, slots=True)
class TaskValidateResultDto:
    """The projection of a task-owned validation outcome."""

    valid: bool
    issues: tuple[str, ...]

    @classmethod
    def from_validation(cls, result) -> TaskValidateResultDto:
        return cls(valid=bool(result.valid), issues=tuple(result.issues))


class TasksAdapter:
    """Adapts the generic task framework + artifact resolver to the CLI.

    ``root`` is the default artifact root used to resolve committed substrate
    releases named by canonical artifact references.
    """

    def __init__(self, registry: ComponentRegistry, *, root: Path = _DEFAULT_ARTIFACT_ROOT) -> None:
        self._registry = registry
        self._root = root

    # -- catalogue ---------------------------------------------
    def list(self) -> tuple[ListedTask, ...]:
        rows = []
        for definition in list_tasks(self._registry):
            rows.append(
                ListedTask(
                    ref=definition.ref.canonical,
                    purpose=definition.purpose,
                    source_roles=tuple(r.role for r in definition.sources.roles),
                    contracts=definition.sources.referenced_contracts,
                )
            )
        return tuple(rows)

    def show(self, task_ref: str) -> TaskShowResult:
        try:
            definition = resolve_task(self._registry, task_ref)
        except (UnknownReferenceError, InvalidReferenceError) as exc:
            raise UnknownTaskError(f"unknown task reference {task_ref!r}") from exc
        except UnsupportedTaskError as exc:
            raise UnknownTaskError(str(exc)) from exc
        return TaskShowResult(
            ref=definition.ref.canonical,
            purpose=definition.purpose,
            source_roles=tuple((r.role, r.required_contract) for r in definition.sources.roles),
            required_contracts=definition.sources.referenced_contracts,
        )

    # -- source resolution -------------------------------------
    def _resolve(self, literal: str):
        """Resolve a canonical artifact reference under the artifact root."""
        try:
            kind, rest = literal.split(":", 1)
            family, variant, rel = rest.split("/")
        except ValueError as exc:
            raise SourceResolutionError(f"malformed artifact reference {literal!r}") from exc
        location = self._root / family / variant / rel
        try:
            return load_release(location)
        except (StoreError, ManifestParseError) as exc:
            raise SourceResolutionError(f"cannot resolve source artifact {literal!r}: {exc}") from exc

    # -- plan ----------------------------------------------
    def plan(
        self,
        task_ref: str,
        sources: tuple[tuple[str, str], ...],
        *,
        release: int,
        seed: int,
    ) -> TaskPlanResult:
        try:
            definition = resolve_task(self._registry, task_ref)
        except (
            UnknownReferenceError,
            InvalidReferenceError,
            UnsupportedTaskError,
        ) as exc:
            raise UnknownTaskError(f"unknown task reference {task_ref!r}") from exc

        resolved: list[tuple[str, str, str]] = []
        for role, literal in sources:
            artifact = self._resolve(literal)
            resolved.append((role, artifact.artifact_ref, artifact.artifact_fingerprint))
        return TaskPlanResult(
            task_ref=definition.ref.canonical,
            resolved_sources=tuple(resolved),
            release=release,
            seed=seed,
            projected_case_count=None,
        )
