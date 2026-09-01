"""Generic task-corpus construction, validation, and inspection machinery.

This package is the framework-owned task layer (``docs/invariants.md``
ARCH-001/ARCH-003). It owns the reusable, task-semantic-free mechanics a task
needs to turn committed source artifacts into a committed, self-contained task
corpus:

* generic task catalogue/discovery over canonical task references;
* source-role binding against framework-owned logical contracts;
* generic construction/validation dispatch through task-owned callables;
* identity, provenance, and staging/commit reuse where applicable.

It deliberately owns **no** scientific task semantics (Stage 6C § 8): it does
not know what a goal, target field, trajectory, revisit, waypoint, or split
means for any concrete task. Those semantics belong to the `ehp_research` task
specifications and are reached exclusively through the registered task
definition instance — never through task-name branching or producer-name
branching.

This package never imports ``ehp_research`` (ARCH-001) and never branches on a
task family name or producer identity.
"""

from __future__ import annotations

from .canonical import SourceRole, TaskDefinition, TaskSourceComposition
from .errors import (
    MissingTaskCapabilityError,
    TaskCompositionError,
    TaskOrchestrationError,
    UnsupportedTaskError,
)
from .orchestration import (
    TaskBuildConfiguration,
    TaskBuildOutcome,
    TaskBuildResult,
    TaskValidateResult,
    build_task_corpus,
    list_tasks,
    resolve_task,
    validate_task_corpus,
)

__all__ = [
    "MissingTaskCapabilityError",
    "SourceRole",
    "TaskBuildConfiguration",
    "TaskBuildOutcome",
    "TaskBuildResult",
    "TaskCompositionError",
    "TaskDefinition",
    "TaskOrchestrationError",
    "TaskSourceComposition",
    "TaskValidateResult",
    "UnsupportedTaskError",
    "build_task_corpus",
    "list_tasks",
    "resolve_task",
    "validate_task_corpus",
]
