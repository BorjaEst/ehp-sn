"""Dagflow substrate family container.

Exposes the authoritative ``substrate:dagflow/v1`` definition object
(``DAGFLOW_DEFINITION``) at the discovery level, and the producer-owned
configuration surface (``resolve_configuration``, ``DagflowConfiguration``,
``DagflowConfigurationError``) and planning capability
(``DagflowPlanningCapability``) with their scientific owner. This package only
re-exports them; it defines no semantics itself.
"""

from __future__ import annotations

from .configuration import (
    DagflowConfiguration,
    DagflowConfigurationError,
    resolve_configuration,
)
from .definition import DAGFLOW_DEFINITION
from .planning import DagflowPlanningCapability

__all__ = [
    "DAGFLOW_DEFINITION",
    "DagflowConfiguration",
    "DagflowConfigurationError",
    "DagflowPlanningCapability",
    "resolve_configuration",
]
