"""Figure framework contract tests (Phase 1 bootstrap slice).

These test :mod:`ehp_sn.figures.contracts`: the ``FigureSpec`` partition
separation and the semantic ``FigureInputRequirement``.

They verify the Phase-1 claims (docs/docs/framework/figures/core.md § ``FigureSpec``;
Phase-1 § 5 · P1-T3, § 7 · P1-T5):

* a ``FigureSpec`` has three observable partitions (projection / visual /
  defaults);
* projection identity is computable without reading the visual or defaults
  partition — the projection partition carries only semantic/preparation
  semantics, never visual or presentation fields;
* an input requirement declares a semantic source role and a logical contract,
  not a producer or physical-storage detail.

No backend selection is needed because these tests never import pyplot.
"""

from __future__ import annotations

from ehp_sn.figures import effective_figure_registry
from ehp_sn.figures.contracts import (
    FIGURE_KIND,
    FigureInputRequirement,
)

_FIGURE_REF = "figure:raster-topology-inspection/v1"


def _spec():
    return effective_figure_registry().resolve(_FIGURE_REF)


# ---------------------------------------------------------------------------
# P1-T3 ordinary-component-catalogue registration (kind figure)
# ---------------------------------------------------------------------------


def test_figure_registers_in_ordinary_catalogue_as_figure_kind() -> None:
    definition = _spec()
    assert definition.kind == FIGURE_KIND == "figure"
    assert definition.ref.canonical == _FIGURE_REF
    assert definition.ref.kind == FIGURE_KIND


# ---------------------------------------------------------------------------
# P1-T5 FigureSpec partition separation
# ---------------------------------------------------------------------------


def test_figure_spec_exposes_three_partitions() -> None:
    spec = _spec()
    # Projection partition: semantic/preparation semantics + prepare.
    assert spec.projection.semantics_version == 1
    assert spec.projection.preparation_version == 1
    assert callable(spec.projection.prepare)
    # Visual partition: visual-semantics version + realization.
    assert spec.visual.semantics_version == 1
    assert callable(spec.visual.realize)
    # Defaults partition: presentation only.
    assert "figure.figsize" in spec.defaults.rc_params


def test_projection_partition_carries_no_visual_or_presentation_state() -> None:
    """Projection identity must be constructible without visual/defaults fields.

    The projection partition of a ``FigureSpec`` holds only requirement,
    semantics versions, and the prepare implementation — never panel/layout,
    profile, serialization, or delivery concepts (Phase-1 § 7 · P1-T5;
    ``core.md`` § "Projection partition").
    """
    projection = _spec().projection
    for field in ("panel", "layout", "profile", "serialization", "visual", "realize"):
        assert not hasattr(projection, field)


# ---------------------------------------------------------------------------
# FigureInputRequirement — semantic source requirement, not storage detail
# ---------------------------------------------------------------------------


def test_input_requirement_declares_role_and_logical_contract() -> None:
    requirement = _spec().projection.requirement
    assert isinstance(requirement, FigureInputRequirement)
    assert requirement.role == "topology"
    assert requirement.contract == "raster-topology/v1"
    # No producer, path, storage-format, or filename detail (Phase-1 § 8 · P1-T6).
    assert not hasattr(requirement, "producer")
    assert not hasattr(requirement, "path")
    assert not hasattr(requirement, "storage_format")
    assert not hasattr(requirement, "filename")


def test_input_requirement_accepts_exact_logical_contract() -> None:
    requirement = FigureInputRequirement(role="topology", contract="raster-topology/v1")
    assert requirement.accepts("raster-topology/v1") is True
    assert requirement.accepts("simple-digraph/v1") is False
