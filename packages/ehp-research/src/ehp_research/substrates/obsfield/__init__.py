"""ObsField substrate family container.

Exposes the authoritative ``substrate:obsfield/v1`` definition object
(``OBSFIELD_DEFINITION``) at the discovery level, and the producer-owned
configuration surface (``resolve_configuration``, ``ObsFieldConfiguration``,
``ObsFieldConfigurationError``), planning resolver (``plan``), and execution
operation (``execute``) with their scientific owner. This package only
re-exports them; it defines no semantics itself.
"""

from __future__ import annotations

from .configuration import (
    Distribution,
    ObsFieldConfiguration,
    ObsFieldConfigurationError,
    resolve_configuration,
)
from .definition import OBSFIELD_DEFINITION
from .execution import execute
from .planning import plan

__all__ = [
    "Distribution",
    "OBSFIELD_DEFINITION",
    "ObsFieldConfiguration",
    "ObsFieldConfigurationError",
    "execute",
    "plan",
    "resolve_configuration",
]
