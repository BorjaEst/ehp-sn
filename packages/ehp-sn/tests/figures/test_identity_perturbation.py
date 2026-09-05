"""Projection/realization identity perturbation matrix (Phase 7C § 10).

These tests make the projection/realization identity *partition* executable for
the rows that neither :mod:`test_projection` nor :mod:`test_figures_realization`
already cover. They close the Phase-7A audit gaps:

* **preparation semantics/version** — changing ``preparation_version`` changes
  both ``ProjectionIdentity`` and ``RealizationIdentity``;
* **projection semantics/version** — changing ``projection_semantics_version``
  changes both identities;
* **scientific visual semantics** — changing ``visual.semantics_version`` leaves
  ``ProjectionIdentity`` unchanged but changes ``RealizationIdentity``
  (Phase-4 · P4-7; ``rendering.md`` § ``RealizationIdentity``);
* **provider enumeration order** — a projection/realization resolved through a
  differently-ordered catalogue shares both identities with the built-in
  catalogue (source-resolution conformance, Phase 7C § 7).

The rows already covered elsewhere (authoritative source identity, authored
selection semantics/parameters, resolved identities, ``RenderProfile``,
serialization request, output path, rendering environment) are intentionally
not re-tested here; they live in :mod:`test_projection`,
:mod:`test_selection_projection`, and :mod:`test_figures_realization`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import matplotlib
import pytest

matplotlib.use("Agg")  # headless backend required for realization rows

from ehp_sn.discovery import ComponentRegistry
from ehp_sn.experiments import ComponentRef
from ehp_sn.figures import (
    FigureInputRequirement,
    effective_figure_registry,
    prepare_figure,
    realize_projection,
    resolve_serialization_policy,
)
from ehp_sn.figures.contracts import (
    FIGURE_KIND,
    _DefaultsPartition,
    _ProjectionPartition,
    _VisualPartition,
)
from ehp_sn.figures.projection import FigureProjection
from ehp_sn.figures.service import _ExactSource

_FIGURE_REF = "figure:perturb/v1"


def _source(*, record_id: str = "sha256:AAA") -> _ExactSource:
    return _ExactSource(
        artifact_ref="artifact:dg/v1",
        record_id=record_id,
        schema_ref="raster-topology/v1",
        content={
            "extent": {"height": 3, "width": 4, "position_count": 12},
            "passable": [True] * 12,
        },
    )


def _noop_realize(projection: FigureProjection) -> object:
    import matplotlib.pyplot as plt

    fig, _ = plt.subplots()
    return fig


@dataclass(frozen=True, slots=True)
class _PerturbableFigure:
    """A synthetic contract-carrier figure with tunable partition versions.

    Lets a test perturb exactly one identity dimension (preparation semantics
    version, projection semantics version, visual semantics version) while every
    other dimension stays fixed, so the projection/realization identity partition
    is asserted against the declared matrix (Phase 7C § 10).
    """

    ref: ComponentRef = field(default_factory=lambda: ComponentRef.parse(_FIGURE_REF))
    kind: str = field(default=FIGURE_KIND)
    projection: _ProjectionPartition = field(
        default_factory=lambda: _ProjectionPartition(
            semantics_version=1,
            preparation_version=1,
            requirement=FigureInputRequirement(role="topo", contract="raster-topology/v1"),
            prepare=lambda source: {"stable": "view"},
        )
    )
    visual: _VisualPartition = field(
        default_factory=lambda: _VisualPartition(semantics_version=1, realize=_noop_realize)
    )
    defaults: _DefaultsPartition = field(default_factory=_DefaultsPartition)


def _perturb_registry(
    *,
    project_semantics_version: int = 1,
    preparation_version: int = 1,
    visual_semantics_version: int = 1,
) -> ComponentRegistry:
    registry = ComponentRegistry()
    registry.register(
        _PerturbableFigure(
            projection=_ProjectionPartition(
                semantics_version=project_semantics_version,
                preparation_version=preparation_version,
                requirement=FigureInputRequirement(role="topo", contract="raster-topology/v1"),
                prepare=lambda source: {"stable": "view"},
            ),
            visual=_VisualPartition(semantics_version=visual_semantics_version, realize=_noop_realize),
        )
    )
    return registry


def _perturb_projection(*, prep_ver: int = 1, proj_ver: int = 1, registry=None) -> FigureProjection:
    reg = (
        registry
        if registry is not None
        else _perturb_registry(project_semantics_version=proj_ver, preparation_version=prep_ver)
    )
    return prepare_figure(reg, _FIGURE_REF, _source())


def _realization(projection, *, registry=None):
    return realize_projection(
        projection,
        serialization=resolve_serialization_policy(format="png"),
        registry=registry,
    )


def test_preparation_semantics_version_changes_both_identities() -> None:
    """Changing preparation semantics/version changes projection and realization id."""
    pa = _perturb_projection(prep_ver=1)
    pb = _perturb_projection(prep_ver=2)
    assert str(pa.identity()) != str(pb.identity())
    ra = _realization(pa, registry=_perturb_registry(preparation_version=1))
    rb = _realization(pb, registry=_perturb_registry(preparation_version=2))
    assert str(ra.realization_identity) != str(rb.realization_identity)


def test_projection_semantics_version_changes_both_identities() -> None:
    """Changing the figure projection semantics/version changes both identities."""
    pa = _perturb_projection(proj_ver=1)
    pb = _perturb_projection(proj_ver=2)
    assert str(pa.identity()) != str(pb.identity())
    ra = _realization(pa, registry=_perturb_registry(project_semantics_version=1))
    rb = _realization(pb, registry=_perturb_registry(project_semantics_version=2))
    assert str(ra.realization_identity) != str(rb.realization_identity)


def test_visual_semantics_version_changes_realization_only() -> None:
    """Changing visual semantics version leaves projection identity unchanged.

    The visual partition is not projection-semantic: two figures that share the
    same projection semantics but differ in visual encoding must share the same
    ``ProjectionIdentity`` but carry different ``RealizationIdentity`` (Phase-4 ·
    P4-7; ``rendering.md`` § ``RealizationIdentity``).
    """
    projection = _perturb_projection(registry=_perturb_registry(visual_semantics_version=1))
    ra = _realization(projection, registry=_perturb_registry(visual_semantics_version=1))
    rb = _realization(projection, registry=_perturb_registry(visual_semantics_version=2))

    # The visual partition does not participate in projection identity.
    assert str(projection.identity()) == str(
        _perturb_projection(registry=_perturb_registry(visual_semantics_version=1)).identity()
    )
    # The visual partition participates in realization identity.
    assert str(ra.realization_identity) != str(rb.realization_identity)


def test_provider_order_same_identity_for_builtin_and_orderings() -> None:
    """A differently-ordered catalogue yields the same projection/realization.

    Catalogue construction must be order-independent (Phase 7C § 7); a projection
    resolved through a fresh ``register_builtin_figures`` registry must share both
    identities with the built-in catalogue (source-resolution conformance).
    """
    registry = ComponentRegistry()
    from ehp_sn.figures import register_builtin_figures

    register_builtin_figures(registry)
    reference = "figure:raster-topology-inspection/v1"
    projection = prepare_figure(registry, reference, _source(record_id="sha256:AAA"))
    baseline = prepare_figure(effective_figure_registry(), reference, _source(record_id="sha256:AAA"))
    assert str(projection.identity()) == str(baseline.identity())
    assert str(_realization(projection, registry=registry).realization_identity) == str(
        _realization(baseline, registry=effective_figure_registry()).realization_identity
    )
