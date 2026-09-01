"""Framework-level task orchestration failures.

These are generic task-layer errors, not CLI errors (the CLI maps them to its
own user-facing categories). They carry no scientific task semantics and never
reference a concrete task family by name.
"""

from __future__ import annotations


class TaskOrchestrationError(Exception):
    """Base class for controlled, framework-level task failures."""


class UnsupportedTaskError(TaskOrchestrationError):
    """A canonical reference is not a registered task definition."""


class MissingTaskCapabilityError(TaskOrchestrationError):
    """A registered task definition lacks the required build/validate capability."""


class TaskCompositionError(TaskOrchestrationError):
    """A task's source-role composition could not be satisfied from the resolved sources."""
