"""Plan-bound execution validation and reporting (Capability 9).

This module establishes the minimal validation/reporting machinery the normative
data-build lifecycle requires **before** producer execution runs: it establishes
that an authoritative :class:`ExecutionPlan` is *executable* — that its target
resolves to a registered substrate definition, that its output contract is
present, and that its immutable identity can be computed for later stages.

It carries the plan identity (:func:`~ehp_sn.planning.plan_identity`) that a
validation report and later lifecycle stages use to refer to one authoritative
plan, so the lifecycle never re-serializes or re-plans. It is deliberately
read-only: validation neither resolves configuration, reselects resources, nor
mutates anything.

The report is not an artifact validator and not a producer validator: it only
checks the plan's structural executability. Producer-specific read, stage, and
commit validation arrive with the artifact lifecycle (later capabilities).
"""

from __future__ import annotations

from dataclasses import dataclass

from ehp_sn.discovery import ComponentRegistry, UnknownReferenceError
from ehp_sn.experiments import InvalidReferenceError
from ehp_sn.planning import ExecutionPlan, plan_identity

#: The component kind the build execution path accepts.
_SUBSTRATE_KIND = "substrate"


class ExecutionValidationError(Exception):
    """The plan is not structurally executable as a substrate build."""


@dataclass(frozen=True, slots=True)
class PlanValidationReport:
    """Read-only outcome of establishing a plan's execution readiness.

    ``plan_id`` is the stable framework identity of the validated plan.
    ``ready`` is ``True`` when the plan is executable as a substrate build; when
    ``False``, ``findings`` lists the human-readable reasons.
    """

    plan_id: str
    ready: bool
    findings: tuple[str, ...]


def validate_execution_plan(
    registry: ComponentRegistry,
    plan: ExecutionPlan,
) -> PlanValidationReport:
    """Return a :class:`PlanValidationReport` for ``plan`` against ``registry``.

    Establishes structural executability: the plan's target is a registered
    substrate definition and the plan carries an output contract. It does not
    require an execution operation to be present (that is the execution
    composition's concern, selected afterward); it only validates the plan. It
    never re-resolves configuration or reselects resources.
    """
    plan_id = plan_identity(plan)
    findings: list[str] = []

    try:
        definition = registry.resolve(plan.target)
    except (UnknownReferenceError, InvalidReferenceError):
        findings.append(
            f"plan target {plan.target.canonical!r} does not resolve to a registered definition"
        )
        return PlanValidationReport(plan_id=plan_id, ready=False, findings=tuple(findings))

    if definition.kind != _SUBSTRATE_KIND:
        findings.append(
            f"plan target {plan.target.canonical!r} is component kind "
            f"{definition.kind!r}, not a substrate"
        )

    if not plan.output_contract:
        findings.append("plan carries no output contract")

    return PlanValidationReport(
        plan_id=plan_id,
        ready=not findings,
        findings=tuple(findings),
    )


__all__ = [
    "ExecutionValidationError",
    "PlanValidationReport",
    "validate_execution_plan",
]
