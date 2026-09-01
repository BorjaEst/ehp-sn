"""MazeHard task definition: the registered, generically-discoverable task.

This module defines :data:`MAZEHARD_DEFINITION` — the authoritative
``task:maze-hard/v1`` definition registered into the generic framework catalogue.
It declares the task's source-role composition (a single ``topology`` role bound
to the framework ``raster-topology/v1`` logical contract) and its generic
build/validate capability, reached by generic orchestration through this
definition instance (never through task-name branching).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from ehp_sn.artifacts import SubstrateArtifact
from ehp_sn.discovery import ComponentRegistry
from ehp_sn.experiments import ComponentRef
from ehp_sn.tasks import (
    SourceRole,
    TaskBuildResult,
    TaskDefinition,
    TaskSourceComposition,
    TaskValidateResult,
)

from .corpus import MazeHardBuilder
from .validation import MazeHardCorpusValidator

#: Canonical task reference: ``task:maze-hard/v1``.
MAZEHARD_REF = ComponentRef(kind="task", name="maze-hard", version=1)

_SOURCES = TaskSourceComposition(
    roles=(SourceRole(role="topology", required_contract="raster-topology/v1"),),
    complete_ambient_compatibility=False,
)


@dataclass(frozen=True, slots=True)
class MazeHardDefinition(TaskDefinition):
    """Registered MazeHard task definition.

    ``kind`` (``task``) must equal ``ref.kind`` (generic registry invariant).
    ``build`` and ``validate`` are the task-owned capabilities the generic
    orchestrator dispatches to; they carry the task's scientific semantics and
    are reached only through this instance.
    """

    ref: ComponentRef
    purpose: str = "full-observation static shortest-route prediction over a raster maze"
    sources: TaskSourceComposition = _SOURCES

    @property
    def kind(self) -> str:
        return self.ref.kind

    def build(self, *, session, sources, configuration, seed) -> TaskBuildResult:
        topology = _topology_source(sources)
        split_policy = _config(configuration, "split_policy", "environment")
        case_role = _config(configuration, "case_role", "test")
        builder = MazeHardBuilder(seed=seed, split_policy=split_policy, case_role=case_role)
        return builder.build(topology)

    def validate(self, *, corpus, sources, configuration) -> TaskValidateResult:
        case_role = _config(configuration, "case_role", "test")
        validator = MazeHardCorpusValidator(case_role=case_role)
        return validator.validate(corpus)


def _topology_source(sources) -> SubstrateArtifact:
    """Extract the sole topology artifact from the bound source tuple."""
    for role, _contract, artifact in sources:
        if role == "topology":
            return cast(SubstrateArtifact, artifact)
    raise ValueError("maze-hard requires a 'topology' source bound to raster-topology/v1")


def _config(configuration, key: str, default):
    if isinstance(configuration, dict):
        return configuration.get(key, default)
    return default


MAZEHARD_DEFINITION = MazeHardDefinition(ref=MAZEHARD_REF)


def register(registry: ComponentRegistry) -> None:
    """Register the MazeHard task definition into ``registry``."""
    registry.register(MAZEHARD_DEFINITION)
