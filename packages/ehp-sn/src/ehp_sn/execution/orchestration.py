"""Generic substrate build execution orchestration (Capability 9).

This module owns the single generic orchestration function that connects an
authoritative :class:`ExecutionPlan` and its producer execution operation (from
the injected :class:`~ehp_sn.execution.composition.SubstrateExecutionComposition`)
to the framework-controlled uncommitted materialization machinery, for one
substrate build execution:

.. code-block:: text

    authoritative ExecutionPlan          (produced exactly once)
        +
    registry                         (definition identity lookup)
        +
    execution composition           (producer operation, injected independently)
        ↓
    establish execution readiness    (read-only validation report)
        ↓
    select execution operation by definition identity
        ↓
    framework-controlled uncommitted materialization session (seeded from plan)
        ↓
    producer scientific execution
        ↓
    populated session (records + auxiliary logical resources)
        ↓
    MaterializationResult            (uncommitted — STOP)

Discovery and execution composition are separate concerns: the registry supplies
only the authoritative definition; the composition supplies the producer's
demonstrated execution operation. Both are injected by the caller; the
orchestration never retrieves producer behavior from the discovery registry.

:func:`execute_substrate` is a single function, not a service class. It is
usable independently of the CLI (a Python caller passes the registry, the
execution composition, and the plan), matching the framework's Python/CLI
equivalence model.

The orchestration is the **uncommitted** phase of the build lifecycle: it
consumes an already-resolved plan, never re-resolves configuration, never
reselected resources, never selects a release coordinate, and never publishes a
final ``SubstrateArtifact``. The producer populates a framework-owned
materialization session; the framework returns the populated session as an
uncommitted result for a later commit capability.
"""

from __future__ import annotations

from dataclasses import dataclass

from ehp_sn.discovery import ComponentRegistry
from ehp_sn.planning import ExecutionPlan

from .composition import SubstrateExecutionComposition
from .materialization import MaterializationSession
from .operation import ExecutionOperation
from .validation import (
    ExecutionValidationError,
    PlanValidationReport,
    validate_execution_plan,
)


class ExecutionError(Exception):
    """A controlled framework execution failure.

    Raised when a substrate build cannot be executed: the plan is not a
    structurally executable substrate build, or no execution operation is bound
    in the injected composition. It is a framework-domain error, not a CLI
    category; the CLI maps it at its own layer.
    """


class MissingExecutionCapabilityError(ExecutionError):
    """A ready plan's target definition has no execution operation in the composition."""


@dataclass(frozen=True, slots=True)
class MaterializationResult:
    """The uncommitted outcome of one substrate build execution.

    ``plan_id`` is the stable framework identity of the consumed plan,
    ``report`` is the read-only readiness report that established the plan was
    executable, and ``materialization`` is the framework-controlled uncommitted
    logical materialization the producer populated. Nothing here is committed or
    published; a later capability closes it into a final ``SubstrateArtifact``.
    """

    plan_id: str
    report: PlanValidationReport
    materialization: MaterializationSession


def execute_substrate(
    registry: ComponentRegistry,
    execution_composition: SubstrateExecutionComposition,
    plan: ExecutionPlan,
) -> MaterializationResult:
    """Execute one substrate build from an authoritative :class:`ExecutionPlan`.

    ``registry`` supplies the authoritative registered definition (resolved by
    the plan's target for identity lookup and composition selection — this is
    identity lookup only, never re-resolving configuration or reselecting
    resources). ``execution_composition`` supplies the producer's demonstrated
    execution operation, selected by definition identity from the resolved
    definition object; it is injected independently of discovery.

    The function:

    1. establishes execution readiness via a read-only validation report;
    2. selects the producer execution operation by definition identity;
    3. seeds a fresh framework-controlled uncommitted materialization session
       from the plan's resolved execution inputs;
    4. invokes the producer operation against the session;
    5. returns the uncommitted :class:`MaterializationResult`.

    Raises :class:`ExecutionValidationError` when the plan is not structurally
    executable as a substrate build, and
    :class:`MissingExecutionCapabilityError` when the composition has no
    execution operation for the plan's target definition.

    This function performs no final artifact publication, selects no release
    coordinate, and writes no committed data.
    """
    report = validate_execution_plan(registry, plan)
    if not report.ready:
        raise ExecutionValidationError(
            f"plan {report.plan_id!r} is not executable as a substrate build: "
            + "; ".join(report.findings)
        )

    definition = registry.resolve(plan.target)
    operation: ExecutionOperation | None = execution_composition.execute(definition)
    if operation is None:
        raise MissingExecutionCapabilityError(
            f"no execution operation in the composition for definition "
            f"{plan.target.canonical!r} (plan {report.plan_id!r})"
        )

    session = MaterializationSession.from_plan(plan)
    operation(session)

    return MaterializationResult(
        plan_id=report.plan_id,
        report=report,
        materialization=session,
    )


__all__ = [
    "ExecutionError",
    "MaterializationResult",
    "MissingExecutionCapabilityError",
    "execute_substrate",
]
