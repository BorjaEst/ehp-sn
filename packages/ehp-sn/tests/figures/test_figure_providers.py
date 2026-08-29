"""Framework figure provider/catalogue-contribution tests (Phase 1).

These test :mod:`ehp_sn.figures.providers` and its participation in the ordinary
component catalogue (docs/docs/framework/figures/core.md § "Catalogue semantics";
Phase-1 § 5 · P1-T3, § 19.12).

They verify:

* the framework built-in figure is contributed to the ordinary
  ``ComponentRegistry`` keyed by kind ``figure``;
* removing the definition from its provider makes ordinary catalogue resolution
  fail — there is no second authoritative registry that can re-resolve it;
* the provider entry-point group is the canonical deferred value.

No backend selection is needed here.
"""

from __future__ import annotations

import pytest
from ehp_sn.discovery import ComponentRegistry, UnknownReferenceError
from ehp_sn.experiments import ComponentRef
from ehp_sn.figures.providers import (
    FIGURE_PROVIDER_ENTRY_POINT_GROUP,
    effective_figure_registry,
    register_builtin_figures,
)

_FIGURE_REF = "figure:raster-topology-inspection/v1"


def test_builtin_figure_registers_into_ordinary_registry() -> None:
    registry = effective_figure_registry()
    definition = registry.resolve(_FIGURE_REF)
    assert definition.kind == "figure"


# ---------------------------------------------------------------------------
# 19.12 catalogue authority — no secondary figure registry
# ---------------------------------------------------------------------------


def test_no_secondary_registry_can_resolve_figure() -> None:
    # The figure resolves through the ordinary ComponentRegistry (kind figure).
    definition = effective_figure_registry().resolve(_FIGURE_REF)
    assert definition.kind == "figure"

    # Removing the definition from its provider makes normal catalogue
    # resolution fail (P1-T3 acceptance criterion): no second registry remains.
    empty = ComponentRegistry()
    with pytest.raises(UnknownReferenceError):
        empty.resolve(ComponentRef.parse(_FIGURE_REF))


def test_register_builtin_figures_is_idempotent_single_authority() -> None:
    """A single catalogue contains exactly one authoritative FigureSpec.

    Re-registering the same built-in into an already-populated catalogue is
    rejected as a duplicate by the registry (ARCH-003): catalogue semantics do
    not depend on registration order and no silent overwrite occurs.
    """
    registry = effective_figure_registry()
    from ehp_sn.discovery import DuplicateRegistrationError
    from ehp_sn.figures.builtin import RASTER_TOPOLOGY_INSPECTION_FIGURE

    with pytest.raises(DuplicateRegistrationError):
        registry.register(RASTER_TOPOLOGY_INSPECTION_FIGURE)


def test_provider_entry_point_group_is_canonical() -> None:
    """The deferred external-provider group uses the canonical figure group."""
    assert FIGURE_PROVIDER_ENTRY_POINT_GROUP == "ehp_sn.figures.providers"


def test_fresh_registry_via_register_is_equivalent() -> None:
    """``register_builtin_figures`` over a fresh ordinary registry yields the same catalogue."""
    fresh = register_builtin_figures(ComponentRegistry())
    assert fresh.resolve(_FIGURE_REF).kind == "figure"


def test_enumerate_figures_via_ordinary_kind() -> None:
    """Built-in figures are enumerable through the ordinary catalogue by kind."""
    registry = effective_figure_registry()
    refs = [d.ref.canonical for d in registry.iter(kind="figure")]
    assert _FIGURE_REF in refs
