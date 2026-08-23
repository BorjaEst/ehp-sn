"""Behavioral tests for the generic framework discovery registry (Phase 3A,
Capability 1).

These tests exercise the framework registration/discovery authority with a
**synthetic in-test definition** — never a runtime research component. The
synthetic definition is deliberately defined inside this test module, not in
``ehp_sn`` production code (``ehp_sn.discovery`` must not contain a fake
substrate).

Both synthetic substrate and synthetic task kinds are used to prove the
registry is genuinely generic: it works identically for any component kind and
never branches on a component family.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from ehp_sn.discovery import (
    ComponentRegistry,
    DiscoverableDefinition,
    DuplicateRegistrationError,
    RegistryError,
    UnknownReferenceError,
)
from ehp_sn.experiments import ComponentRef, InvalidReferenceError


@dataclass(frozen=True)
class SyntheticDefinition:
    """Minimal in-test discoverable definition.

    Intentionally as small as the discovery protocol requires: a canonical
    reference and a component kind. No substrate/task semantics are attached.
    """

    ref: ComponentRef
    kind: str


def synthetic(ref_text: str) -> SyntheticDefinition:
    """Build a synthetic definition from a canonical reference text."""
    ref = ComponentRef.parse(ref_text)
    return SyntheticDefinition(ref=ref, kind=ref.kind)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def test_register_one_definition_succeeds() -> None:
    registry = ComponentRegistry()
    definition = synthetic("substrate:synthetic/v1")

    registry.register(definition)

    assert registry.contains("substrate:synthetic/v1")


def test_register_different_references_succeeds() -> None:
    registry = ComponentRegistry()
    a = synthetic("substrate:synthetic/v1")
    b = synthetic("task:synthetic/v1")

    registry.register(a)
    registry.register(b)

    assert registry.contains(a.ref)
    assert registry.contains(b.ref)


def test_register_same_canonical_reference_twice_rejected() -> None:
    registry = ComponentRegistry()
    first = synthetic("substrate:synthetic/v1")
    second = synthetic("substrate:synthetic/v1")

    registry.register(first)
    with pytest.raises(DuplicateRegistrationError):
        registry.register(second)

    # The first definition remains authoritative and is not replaced.
    assert registry.resolve("substrate:synthetic/v1") is first


def test_register_does_not_modify_definition() -> None:
    registry = ComponentRegistry()
    definition = synthetic("substrate:synthetic/v1")

    registry.register(definition)

    assert definition.ref == ComponentRef.parse("substrate:synthetic/v1")
    assert definition.kind == "substrate"


def test_register_does_not_store_copied_metadata() -> None:
    registry = ComponentRegistry()
    definition = synthetic("task:synthetic/v1")

    registry.register(definition)

    # Identity, not a shallow copy or a parallel metadata descriptor.
    assert registry.resolve(definition.ref) is definition


def test_register_rejects_kind_mismatch_with_reference() -> None:
    registry = ComponentRegistry()
    definition = SyntheticDefinition(ref=ComponentRef.parse("task:synthetic/v1"), kind="substrate")

    with pytest.raises(RegistryError):
        registry.register(definition)


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------


def test_resolve_returns_same_object() -> None:
    registry = ComponentRegistry()
    definition = synthetic("substrate:synthetic/v1")
    registry.register(definition)

    assert registry.resolve("substrate:synthetic/v1") is definition
    assert registry.resolve(definition.ref) is definition


def test_resolve_unknown_reference_raises() -> None:
    registry = ComponentRegistry()
    registry.register(synthetic("substrate:synthetic/v1"))

    with pytest.raises(UnknownReferenceError):
        registry.resolve("substrate:missing/v1")


def test_resolve_malformed_reference_delegates_to_reference_subsystem() -> None:
    registry = ComponentRegistry()

    # The registry must not invent its own parser: malformed references are
    # rejected by the reference subsystem, not by registry code.
    with pytest.raises(InvalidReferenceError):
        registry.resolve("not-a-reference")


# ---------------------------------------------------------------------------
# Enumeration
# ---------------------------------------------------------------------------


def test_iter_returns_all_kinds_in_canonical_order() -> None:
    registry = ComponentRegistry()
    # Register in deliberately non-canonical order.
    substrate_b = synthetic("substrate:b/v1")
    task_a = synthetic("task:a/v1")
    substrate_a = synthetic("substrate:a/v1")
    for d in (substrate_b, task_a, substrate_a):
        registry.register(d)

    resolved = list(registry.iter())

    assert resolved == [substrate_a, substrate_b, task_a]


def test_iter_filters_by_kind_in_canonical_order() -> None:
    registry = ComponentRegistry()
    substrate_b = synthetic("substrate:b/v1")
    task_a = synthetic("task:a/v1")
    substrate_a = synthetic("substrate:a/v1")
    for d in (substrate_b, task_a, substrate_a):
        registry.register(d)

    substrates = list(registry.iter(kind="substrate"))

    assert substrates == [substrate_a, substrate_b]


def test_iter_filters_unknown_kind_to_empty() -> None:
    registry = ComponentRegistry()
    registry.register(synthetic("substrate:a/v1"))

    assert list(registry.iter(kind="model")) == []


# ---------------------------------------------------------------------------
# Genericity — the registry must be genuinely generic.
# ---------------------------------------------------------------------------


def test_generic_registry_works_for_substrate_and_task() -> None:
    registry = ComponentRegistry()
    substrate = synthetic("substrate:synthetic/v1")
    task = synthetic("task:synthetic/v1")

    registry.register(substrate)
    registry.register(task)

    assert list(registry.iter()) == [substrate, task]
    assert list(registry.iter(kind="substrate")) == [substrate]
    assert list(registry.iter(kind="task")) == [task]
    assert registry.resolve("substrate:synthetic/v1") is substrate
    assert registry.resolve("task:synthetic/v1") is task


def test_registry_source_contains_no_research_or_family_branching() -> None:
    """Guards the strong Capability 1 acceptance criterion.

    The registry module must not import ``ehp_research``, must not branch on a
    component family/substrate name, and must remain meaningful with no
    concrete component present.
    """
    import inspect
    import pathlib

    from ehp_sn import discovery as discovery_package

    source_root = pathlib.Path(discovery_package.__file__).resolve().parent
    registry_source = (source_root / "registry.py").read_text(encoding="utf-8")

    # The guard is about *behavior* — no research import, no data import, no
    # family branching — not about the words appearing in prose/docstrings.
    # Scan only import statements and family-name tokens in code.
    import_lines = [
        line for line in registry_source.splitlines() if line.lstrip().startswith(("import ", "from "))
    ]
    assert not any("ehp_research" in line for line in import_lines)
    assert not any("ehp_sn.data" in line for line in import_lines)
    # Family branching: no literal dagflow/maze-nd tokens anywhere in the file.
    assert "dagflow" not in registry_source.lower()
    assert "maze-nd" not in registry_source.lower()

    # The definition protocol is implemented (and runtime-checkable) purely in
    # terms of ref + kind.
    assert inspect.isabstract(DiscoverableDefinition) is False


def test_registry_works_with_runtime_protocol_check() -> None:
    """A definition need not subclass anything; structural conformance suffices."""
    registry = ComponentRegistry()
    definition = synthetic("substrate:synthetic/v1")

    assert isinstance(definition, DiscoverableDefinition)
    registry.register(definition)
    assert registry.resolve("substrate:synthetic/v1") is definition


# ---------------------------------------------------------------------------
# Definition-only authority
#
# The registry owns discoverable definitions, not behavior. Registration has no
# behavioral parameter, and the registry exposes no capability/resolver/
# behavior lookup. Producer planning is composed outside discovery.
# ---------------------------------------------------------------------------


def test_registry_has_no_behavioral_registration_parameter() -> None:
    """``register`` accepts only a definition — no capability/resolver argument.

    Guards the invariant that discovery is definition-only: behavior is
    associated through the planning composition, never on the registry entry.
    """
    signature = ComponentRegistry.register.__annotations__
    # Only ``definition`` (plus ``self``/return) is declared; no ``capability``,
    # ``behavior``, ``resolver``, ``provider``, or ``metadata`` parameter exists.
    declared = {name for name in signature if name not in {"return"}}
    assert declared <= {"definition"}

    # No behavioral lookup methods are exposed on the registry.
    assert not hasattr(ComponentRegistry, "capability")
    assert not hasattr(ComponentRegistry, "register_capability")
    assert not hasattr(ComponentRegistry, "planning_capability")
    assert not hasattr(ComponentRegistry, "register_planning_capability")
    assert not hasattr(ComponentRegistry, "has_capability")
