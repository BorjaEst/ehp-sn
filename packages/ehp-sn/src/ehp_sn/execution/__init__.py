"""Generic framework substrate build execution.

This package owns the generic, framework-level execution surface for one
substrate build: the framework record-identity mechanism, the framework-
controlled uncommitted logical materialization boundary, the narrow typed
producer execution operation, the producer execution composition, the plan-bound
execution validation/reporting, and the single execution orchestration function.

It is the execution counterpart of ``ehp_sn.planning`` and follows the same
discipline: it composes a demonstrated producer execution operation with a
registered definition independently of discovery, consumes an authoritative
:class:`~ehp_sn.planning.ExecutionPlan` exactly once, and never resolves a
producer configuration or reselects resources.

Capability 9 deliberately stops before final artifact publication: execution
produces an uncommitted :class:`MaterializationResult` that a later capability
closes into a committed ``SubstrateArtifact``. ``ehp_sn`` never imports a
concrete research package and never branches on a substrate family
(``ARCH-001``/``ARCH-003``).
"""

from __future__ import annotations

from .composition import (
    PROVIDER_ENTRY_POINT_GROUP,
    SubstrateExecutionComposition,
    SubstrateExecutionRegistration,
    compose_execution_providers,
    effective_execution_composition,
)
from .materialization import (
    GeneratedRecordBody,
    LogicalRecord,
    LogicalResource,
    MaterializationSession,
)
from .operation import ExecutionOperation
from .orchestration import (
    ExecutionError,
    MaterializationResult,
    MissingExecutionCapabilityError,
    execute_substrate,
)
from .record_identity import RealizationKey, derive_record_id, realization_key_value
from .validation import (
    ExecutionValidationError,
    PlanValidationReport,
    validate_execution_plan,
)

__all__ = [
    "PROVIDER_ENTRY_POINT_GROUP",
    "ExecutionError",
    "ExecutionOperation",
    "ExecutionValidationError",
    "GeneratedRecordBody",
    "LogicalRecord",
    "LogicalResource",
    "MaterializationResult",
    "MaterializationSession",
    "MissingExecutionCapabilityError",
    "PlanValidationReport",
    "RealizationKey",
    "SubstrateExecutionComposition",
    "SubstrateExecutionRegistration",
    "compose_execution_providers",
    "derive_record_id",
    "effective_execution_composition",
    "execute_substrate",
    "realization_key_value",
    "validate_execution_plan",
]
