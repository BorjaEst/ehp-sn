"""Generic framework planning.

This package owns the generic, framework-level planning surface: the narrow
typed producer planning operation, the producer planning composition, the
immutable plan, logical resource requirements and their resolution, and the
single planning orchestration function. Discovery of definitions is owned
elsewhere (``ehp_sn.discovery``); this package composes the demonstrated
producer planning operation with a registered definition independently of it.

It is deliberately reusable and not data-specific: the immutable plan, resource
requirement, and identity-input representations are generic framework contracts
instantiated here for the first time, and later planning paths (for example
task corpora) reuse them. ``ehp_sn`` never imports a concrete research package
and never branches on a substrate family (``ARCH-001``/``ARCH-003``).
"""

from __future__ import annotations

from .capability import PlanningDeclaration, PlanningResolver
from .composition import (
    PROVIDER_ENTRY_POINT_GROUP,
    SubstratePlanningComposition,
    SubstratePlanningRegistration,
    compose_planning_providers,
    effective_planning_composition,
)
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
    "PROVIDER_ENTRY_POINT_GROUP",
    "PlanningDeclaration",
    "PlanningError",
    "PlanningResolver",
    "ProducerResolutionError",
    "ResolvedResource",
    "ResourceResolutionError",
    "ResourceRequirement",
    "ResourceResolver",
    "SubstratePlanningComposition",
    "SubstratePlanningRegistration",
    "compose_planning_providers",
    "effective_planning_composition",
    "plan_substrate",
]
