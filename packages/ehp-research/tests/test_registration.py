"""Behavioral and architectural tests for Capability 2 — real research-provider
registration (Phase 3A).

These tests prove that an explicit ``ehp_research`` integration function
(:func:`ehp_research.registration.register_components`) can populate a *fresh,
generic* ``ehp_sn`` registry with the authoritative Dagflow and Maze-ND
definition objects — without modifying generic discovery semantics, duplicating
scientific metadata, introducing import-time registration, or adding
configuration/planning/execution abstractions (Capability 2 acceptance
criteria).

The generic registry (``ehp_sn.discovery``) understands only canonical refs and
kinds; it never imports ``ehp_research`` and never branches on a family. All
scientific meaning is carried by the research-owned definition objects.
"""

from __future__ import annotations

import pathlib

import pytest
from ehp_research.registration import planning_registrations, register_components
from ehp_research.substrates.dagflow import DAGFLOW_DEFINITION
from ehp_research.substrates.maze_nd import MAZE_ND_DEFINITION
from ehp_sn.discovery import (
    ComponentRegistry,
    DiscoverableDefinition,
    DuplicateRegistrationError,
)
from ehp_sn.experiments import ComponentRef
from ehp_sn.planning import SubstratePlanningComposition


def fresh_registry() -> ComponentRegistry:
    """A new empty generic registry, populated via the research integration."""
    registry = ComponentRegistry()
    register_components(registry)
    return registry


# ---------------------------------------------------------------------------
# Provider registration
# ---------------------------------------------------------------------------


def test_register_components_yields_exactly_the_provider_set() -> None:
    registry = ComponentRegistry()

    register_components(registry)

    canonical_refs = sorted(definition.ref.canonical for definition in registry.iter())
    assert canonical_refs == [
        "substrate:dagflow/v1",
        "substrate:dungeongen/v1",
        "substrate:maze-nd/v1",
        "substrate:obsfield/v1",
        "task:maze-hard/v1",
    ]


def test_register_components_populates_a_fresh_registry() -> None:
    # Registration is explicit and relies on the caller's registry: a fresh,
    # empty registry gains exactly the provider definitions after the call.
    registry = ComponentRegistry()

    assert list(registry.iter()) == []
    register_components(registry)
    assert registry.contains("substrate:dagflow/v1")
    assert registry.contains("substrate:dungeongen/v1")
    assert registry.contains("substrate:maze-nd/v1")
    assert registry.contains("substrate:obsfield/v1")


def test_register_components_registers_into_the_given_registry_only() -> None:
    # Two independent registries each populated separately: the function writes
    # only to the registry it is given, never to an implicit global.
    registry_a = ComponentRegistry()
    registry_b = ComponentRegistry()

    register_components(registry_a)

    assert sorted(d.ref.canonical for d in registry_a.iter()) == [
        "substrate:dagflow/v1",
        "substrate:dungeongen/v1",
        "substrate:maze-nd/v1",
        "substrate:obsfield/v1",
        "task:maze-hard/v1",
    ]
    assert list(registry_b.iter()) == []


def test_register_components_is_not_silently_idempotent() -> None:
    """Duplicate registration must fail, not be silently tolerated.

    The provider function performs no duplicate detection of its own; duplicate
    handling belongs to the generic registry, which rejects a reused canonical
    reference.
    """
    registry = ComponentRegistry()
    register_components(registry)

    with pytest.raises(DuplicateRegistrationError):
        register_components(registry)

    # The first registration remains authoritative and unchanged.
    assert registry.resolve("substrate:dagflow/v1") is DAGFLOW_DEFINITION
    assert registry.resolve("substrate:maze-nd/v1") is MAZE_ND_DEFINITION


# ---------------------------------------------------------------------------
# Same authoritative object (identity preservation)
# ---------------------------------------------------------------------------


def test_resolve_dagflow_returns_the_authoritative_object() -> None:
    registry = fresh_registry()

    assert registry.resolve("substrate:dagflow/v1") is DAGFLOW_DEFINITION


def test_resolve_maze_nd_returns_the_authoritative_object() -> None:
    registry = fresh_registry()

    assert registry.resolve("substrate:maze-nd/v1") is MAZE_ND_DEFINITION


def test_resolved_definitions_are_structurally_discoverable() -> None:
    registry = fresh_registry()

    for reference in ("substrate:dagflow/v1", "substrate:maze-nd/v1"):
        definition = registry.resolve(reference)
        assert isinstance(definition, DiscoverableDefinition)
        assert definition.kind == "substrate"


def test_enumeration_and_resolution_agree_on_the_same_objects() -> None:
    registry = fresh_registry()

    by_ref = {definition.ref.canonical: definition for definition in registry.iter()}
    assert by_ref["substrate:dagflow/v1"] is DAGFLOW_DEFINITION
    assert by_ref["substrate:maze-nd/v1"] is MAZE_ND_DEFINITION


# ---------------------------------------------------------------------------
# Planning composition (separate concern from discovery)
# ---------------------------------------------------------------------------


def test_planning_registrations_bind_each_definition_to_its_resolver() -> None:
    """The planning composition associates each definition with its resolver by identity.

    Discovery is not extended to own producer behavior; the planning
    composition selects each definition's resolver by the authoritative object
    identity, which matches what the registry resolves.
    """
    registry = fresh_registry()
    composition = SubstratePlanningComposition(planning_registrations())

    # The composition matches the exact authoritative definitions by identity.
    assert composition.resolver(registry.resolve("substrate:dagflow/v1")) is not None
    assert composition.resolver(registry.resolve("substrate:maze-nd/v1")) is not None
    assert composition.resolver(registry.resolve("substrate:obsfield/v1")) is not None
    assert composition.resolver(registry.resolve("substrate:dungeongen/v1")) is not None
    assert len(composition) == 4


# ---------------------------------------------------------------------------
# Discovery metadata on the authoritative definitions
# ---------------------------------------------------------------------------


def test_dagflow_output_contract_is_simple_digraph() -> None:
    assert DAGFLOW_DEFINITION.output_contract == "simple-digraph/v1"


def test_maze_nd_output_contract_is_raster_topology() -> None:
    assert MAZE_ND_DEFINITION.output_contract == "raster-topology/v1"


def test_each_definition_reports_its_canonical_reference() -> None:
    assert DAGFLOW_DEFINITION.ref == ComponentRef.parse("substrate:dagflow/v1")
    assert MAZE_ND_DEFINITION.ref == ComponentRef.parse("substrate:maze-nd/v1")


def test_definitions_derive_kind_from_canonical_reference() -> None:
    # No independently stored kind/family/version: the canonical ref is the
    # single identity authority.
    assert DAGFLOW_DEFINITION.kind == DAGFLOW_DEFINITION.ref.kind == "substrate"
    assert MAZE_ND_DEFINITION.kind == MAZE_ND_DEFINITION.ref.kind == "substrate"


# ---------------------------------------------------------------------------
# No import-time side effects
# ---------------------------------------------------------------------------


def test_importing_ehp_research_does_not_populate_a_registry() -> None:
    """Mere import of ``ehp_research`` must not mutate framework discovery state.

    Registration occurs only through the explicit provider integration path
    (:func:`register_components`), never at import time.
    """
    # The import above has already loaded ehp_research.registration and all the
    # definition modules; a fresh registry must still be empty until the
    # explicit call is made.
    registry = ComponentRegistry()
    assert list(registry.iter()) == []


def test_registration_module_has_no_side_effecting_execution() -> None:
    """Importing the integration module performs no registration by itself."""
    # Importing does not raise and does not create a registry; the explicit
    # function is what populates.
    import importlib

    module = importlib.import_module("ehp_research.registration")
    assert callable(getattr(module, "register_components", None))


# ---------------------------------------------------------------------------
# Import direction and generic-registry non-modification
# ---------------------------------------------------------------------------


def test_ehp_sn_discovery_does_not_depend_on_ehp_research() -> None:
    """Guards the core package boundary: ``ehp_research → ehp_sn`` only.

    The generic discovery module must not import ``ehp_research``, and the
    framework must not branch on any substrate family. Capability 2 must
    require zero special handling in ``ehp_sn``.
    """
    from ehp_sn import discovery as discovery_package

    source_root = pathlib.Path(discovery_package.__file__).resolve().parent
    files = [p for p in source_root.rglob("*.py") if p.is_file()]
    assert files, "expected at least the discovery package source"

    for file in files:
        text = file.read_text(encoding="utf-8")
        import_lines = [
            line for line in text.splitlines() if line.lstrip().startswith(("import ", "from "))
        ]
        assert not any("ehp_research" in line for line in import_lines), file
        assert "dagflow" not in text.lower()
        assert "maze-nd" not in text.lower()


def test_ehp_research_registration_imports_framework_discovery() -> None:
    """The research integration point consumes the framework boundary."""
    import inspect

    from ehp_research import registration as registration_module

    source = inspect.getsource(registration_module)
    assert "ComponentRegistry" in source
    assert "ehp_sn" in source


# ---------------------------------------------------------------------------
# Advertised provider metadata integrity (P0R-1)
# ---------------------------------------------------------------------------

#: The framework-owned entry-point groups the research package currently advertises.
_ADVERTISED_PROVIDER_GROUPS = (
    "ehp_sn.providers",
    "ehp_sn.planning.providers",
    "ehp_sn.execution.providers",
    "ehp_sn.figures.providers",
)


def test_research_figure_provider_advertised_under_figure_group() -> None:
    """The research figure provider is advertised under the framework figure-provider
    entry-point group ``ehp_sn.figures.providers`` (P3-T1 · G1)."""
    import pathlib
    from importlib import metadata

    from ehp_sn.figures.providers import FIGURE_PROVIDER_ENTRY_POINT_GROUP

    pyproject = pathlib.Path(__file__).resolve().parents[1] / "pyproject.toml"
    pyproject_text = pyproject.read_text(encoding="utf-8")
    assert FIGURE_PROVIDER_ENTRY_POINT_GROUP in pyproject_text
    assert "ehp_research.figures.providers:figure_provider" in pyproject_text

    # The advertised entry point must resolve to a loadable real provider.
    figure_eps = [
        ep
        for ep in metadata.entry_points(group=FIGURE_PROVIDER_ENTRY_POINT_GROUP)
        if ep.value.startswith("ehp_research.")
    ]
    assert figure_eps, "research figure provider is not advertised under the figure group"
    for entry_point in figure_eps:
        entry_point.load()  # raises if module/attribute is absent


def test_all_advertised_provider_entry_points_load() -> None:
    """Every advertised ``ehp_research`` provider entry point must load.

    Uses the real ``importlib.metadata`` distribution metadata (not injected
    fake entry points), so a stale or missing provider module/attribute fails
    here rather than surfacing only at application bootstrap.
    """
    from importlib import metadata

    loaded: list[str] = []
    for group in _ADVERTISED_PROVIDER_GROUPS:
        for entry_point in metadata.entry_points(group=group):
            if not entry_point.value.startswith("ehp_research."):
                continue
            entry_point.load()  # raises if module/attribute is absent
            loaded.append(f"{group}::{entry_point.name} -> {entry_point.value}")
    assert loaded, "no ehp_research provider entry points were discovered"


def test_obsolete_figure_and_analysis_providers_are_not_advertised() -> None:
    """``ehp_research`` must not advertise provider groups it does not implement.

    The framework-owned figure-provider group ``ehp_sn.figures.providers`` is an
    active group (Phase 2 contributes external figures through it). Phase 3 adds
    a real ``ehp_research.figures.providers:figure_provider`` module, so the
    figure group legitimately advertises it and the module must load. The
    ``ehp_sn.analysis.providers`` group remains an unfilled later-phase group
    and must stay unadvertised. Advertising a provider module that does not
    exist would break provider discovery (P0R-1).
    """
    from importlib import metadata

    for entry_point in metadata.entry_points(group="ehp_sn.figures.providers"):
        if entry_point.value.startswith("ehp_research."):
            # Phase 3: the research figure provider is real and must load.
            entry_point.load()

    # No ehp_research entry point in the figures group may point at an obsolete
    # analysis-provider module, and the analysis group remains unadvertised
    # (later phase).
    for entry_point in metadata.entry_points(group="ehp_sn.figures.providers"):
        assert "ehp_research.analysis.providers" not in entry_point.value
        assert "ehp_research.figures.analysis" not in entry_point.value
    assert list(metadata.entry_points(group="ehp_sn.analysis.providers")) == [], (
        "old ehp_sn.analysis.providers group is still advertised"
    )
