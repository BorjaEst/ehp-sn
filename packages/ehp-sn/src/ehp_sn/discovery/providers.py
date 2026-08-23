"""Generic composition of installed providers into an application registry.

This module is the framework-owned bootstrap that answers one question: how does
an application (for example, the CLI) obtain the *effective* registry containing
every installed research package's registered definitions — without the
framework importing any concrete research package by name and without a
``try/except ImportError`` fallback?

The mechanism is the standard Python entry-point provider pattern
(``importlib.metadata``):

1. the framework defines an entry-point *group* (``ehp_sn.providers``);
2. a downstream package (for example ``ehp_research``) advertises a provider
   function under that group whose signature is ``(ComponentRegistry) -> None``
   and which registers the definitions it owns;
3. :func:`effective_registry` builds a fresh registry, discovers every installed
   provider under the group, and calls each with the registry.

This keeps the dependency direction ``ehp_research → ehp_sn`` intact and lets
the framework stay independent of concrete research packages (ARCH-001/ARCH-003).
Providers own their registered definitions; the registry itself enumerates
deterministically and rejects conflicting duplicates, so provider/registration
order is not part of the scientific contract.

No configuration, planning, execution, or lifecycle semantics live here. This is
only the composition root that connects installed providers to a registry.
"""

from __future__ import annotations

from importlib import metadata

from .registry import ComponentRegistry

#: Entry-point group under which installed packages advertise provider functions.
#
#: A provider is a callable ``(ComponentRegistry) -> None`` that registers the
#: definitions it owns into the given registry.
PROVIDER_ENTRY_POINT_GROUP = "ehp_sn.providers"


def register_installed_providers(
    registry: ComponentRegistry,
    *,
    group: str = PROVIDER_ENTRY_POINT_GROUP,
) -> ComponentRegistry:
    """Populate ``registry`` by invoking every installed provider under ``group``.

    Each provider entry point is loaded (which imports the owning module) and
    called with ``registry``. Providers register their definitions into it.
    Returns ``registry`` so callers can chain or pass it directly to a consumer.

    Ordering across providers is intentionally not part of the contract: the
    registry enumerates registered definitions deterministically (ARCH-003).
    """
    for entry_point in metadata.entry_points(group=group):
        provider = entry_point.load()
        provider(registry)
    return registry


def effective_registry(
    *,
    group: str = PROVIDER_ENTRY_POINT_GROUP,
) -> ComponentRegistry:
    """Build and return the effective application registry.

    A fresh :class:`ComponentRegistry` is populated with every installed
    provider under ``group`` and returned. An application constructs this once
    and injects it into consumers (for example, an adapter) rather than each
    consumer performing its own discovery.
    """
    return register_installed_providers(ComponentRegistry(), group=group)


__all__ = [
    "PROVIDER_ENTRY_POINT_GROUP",
    "effective_registry",
    "register_installed_providers",
]
