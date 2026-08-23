"""Generic framework planning (Capability 6).

This package owns the generic, framework-level planning surface: the narrow
producer planning capability boundary, the immutable plan, logical resource
requirements and their resolution, and the single planning orchestration
function.

It is deliberately reusable and not data-specific: the immutable plan, resource
requirement, and identity-input representations are generic framework contracts
instantiated here for the first time, and later planning paths (for example
task corpora) reuse them. ``ehp_sn`` never imports a concrete research package
and never branches on a substrate family (``ARCH-001``/``ARCH-003``).
"""

from __future__ import annotations

from .capability import PlanningDeclaration, SubstratePlanningCapability
from .identity import IdentityInput
from .orchestration import (
    MissingPlanningCapabilityError,
    NotASubstrateError,
    PlanningError,
    ProducerResolutionError,
    plan_substrate,
)
from .plan import ExecutionPlan
from .resources import (
    CARDINALITY_ONE,
    CARDINALITY_OPTIONAL_ONE,
    ResolvedResource,
    ResourceRequirement,
    ResourceResolutionError,
    ResourceResolver,
)

__all__ = [
    "CARDINALITY_ONE",
    "CARDINALITY_OPTIONAL_ONE",
    "ExecutionPlan",
    "IdentityInput",
    "MissingPlanningCapabilityError",
    "NotASubstrateError",
    "PlanningDeclaration",
    "PlanningError",
    "ProducerResolutionError",
    "ResolvedResource",
    "ResourceResolutionError",
    "ResourceRequirement",
    "ResourceResolver",
    "SubstratePlanningCapability",
    "plan_substrate",
]
