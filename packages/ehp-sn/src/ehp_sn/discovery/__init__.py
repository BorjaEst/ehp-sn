"""Generic framework component registration and discovery.

This package is the framework-owned registration/discovery interface
(``docs/invariants.md`` ARCH-001/ARCH-003): installed research definitions
register against framework-owned registries rather than each package
maintaining its own catalogue.

It is deliberately generic. It understands component references, component
kinds, and registered definitions — not substrates, tasks, models, or CLI
commands. No component-family-specific logic lives here.
"""

from __future__ import annotations

from .registry import (
    ComponentRegistry,
    DiscoverableDefinition,
    DuplicateRegistrationError,
    RegistryError,
    UnknownReferenceError,
)

__all__ = [
    "ComponentRegistry",
    "DiscoverableDefinition",
    "DuplicateRegistrationError",
    "RegistryError",
    "UnknownReferenceError",
]
