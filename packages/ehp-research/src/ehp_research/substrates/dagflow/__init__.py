"""Dagflow substrate family container.

Exposes the authoritative ``substrate:dagflow/v1`` definition object
(``DAGFLOW_DEFINITION``) at the discovery level, and the producer-owned
configuration surface (``resolve_configuration``, ``DagflowConfiguration``,
``DagflowConfigurationError``) from ``configuration.py`` with its scientific
owner. This package only re-exports them; it defines no semantics itself.
"""

from __future__ import annotations

from .configuration import (
    DagflowConfiguration,
    DagflowConfigurationError,
    resolve_configuration,
)
from .definition import DAGFLOW_DEFINITION

__all__ = [
    "DAGFLOW_DEFINITION",
    "DagflowConfiguration",
    "DagflowConfigurationError",
    "resolve_configuration",
]
