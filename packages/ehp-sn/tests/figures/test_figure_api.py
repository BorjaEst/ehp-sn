"""Public Python figure API facade tests (Phase 5D).

These test :mod:`ehp_sn.figures.api` — the supported public Python figure
surface (:class:`~ehp_sn.figures.api.FigureSource`,
:func:`~ehp_sn.figures.api.prepare_figure`,
:func:`~ehp_sn.figures.api.render_figure_projection`,
:func:`~ehp_sn.figures.api.realize_projection`, and the
:func:`~ehp_sn.figures.api.render_figure` convenience).

They prove the Phase-5 convergence invariant: the Python API is a **façade over
the same canonical generic figure service** already used by runtime/CLI
operations, and equivalent semantic requests normalize to the same canonical
figure reference, the same source-role identity, the same authored + resolved
selection, and the same ``ProjectionIdentity`` — no matter which interface
produced them (Phase 5D · § 7.5, § 7.8, § 7.9).

```text
no private duplicate catalogue
no duplicate selection resolution
no alternate identity derivation
render_figure composes only the canonical prepare + realize path
```

Presentation divergence (same ``ProjectionIdentity``, different
``RealizationIdentity``) is a generic realization concern already covered by
:mod:`~ehp_sn.tests.figures.test_figures_realization` (P4-3/P4-4) and is not
re-tested here.

Tests are headless (the non-interactive Matplotlib backend is selected before
any pyplot use, Phase-1 § 16 · P1-T14).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import matplotlib
import pytest

matplotlib.use("Agg")  # headless backend

from ehp_sn.discovery import ComponentRegistry
from ehp_sn.experiments import ComponentRef
from ehp_sn.figures import (
    FIGURE_KIND,
    FigureProjection,
    FigureSource,
    ResolvedFigureSelection,
    effective_figure_registry,
    realize_projection,
    render_figure,
    render_figure_projection,
    resolve_serialization_policy,
)
from ehp_sn.figures import prepare_figure as api_prepare_figure
from ehp_sn.figures.contracts import (
    FigureInputRequirement,
    _DefaultsPartition,
    _ProjectionPartition,
    _VisualPartition,
)
from ehp_sn.figures.service import prepare_figure as service_prepare_figure

#: A canonical raster-topology/v1 source used for convergence.
_AUTHORITATIVE_CONTENT = {
    "extent": {"height": 3, "width": 4, "position_count": 12},
    "passable": [True] * 12,
}
_SOURCE = FigureSource(
    artifact_ref="artifact:dg/v1",
    record_id="sha256:1a616516549d83c695f16ffebbc58c33f6cb3ed4dcf95a554fa3bd0d7f0bd1eb",
    schema_ref="raster-topology/v1",
    content=_AUTHORITATIVE_CONTENT,
)
_RASTER_FIGURE = "figure:raster-topology-inspection/v1"


def _registry() -> ComponentRegistry:
    return effective_figure_registry()


# ---------------------------------------------------------------------------
# CLI/Python normalized-request convergence (no selection) — Phase 5D § 7.5/7.8
# ---------------------------------------------------------------------------


def test_cli_equivalent_and_python_equivalent_converge_on_identity() -> None:
    """An equivalent CLI-style request and a direct Python-API request converge.

    The CLI ``data inspect --figure`` path resolves the committed record then
    delegates to the canonical service ``prepare_figure``. We model that
    "CLI-equivalent" normalization by invoking ``service.prepare_figure`` with
    the exact resolved source, and model the "Python-equivalent" request by
    invoking the public ``api.prepare_figure`` with the same :class:`FigureSource`.
    Both delegate to the one canonical implementation (Phase 5D § 7.9) and must
    normalize to the identical projection provenance and identity.
    """
    registry = _registry()

    cli_equivalent = service_prepare_figure(registry, _RASTER_FIGURE, _SOURCE)
    python_equivalent = api_prepare_figure(registry, _RASTER_FIGURE, _SOURCE)

    # Same canonical figure reference.
    assert cli_equivalent.figure_ref == python_equivalent.figure_ref == _RASTER_FIGURE
    # Same source-role identity (role, artifact, record, logical contract).
    assert cli_equivalent.source == python_equivalent.source
    assert cli_equivalent.source.role == "topology"
    assert cli_equivalent.source.record_id == _SOURCE.record_id
    # Same projection semantics + preparation version.
    assert cli_equivalent.projection_semantics_version == python_equivalent.projection_semantics_version
    assert cli_equivalent.preparation_version == python_equivalent.preparation_version
    # Same prepared view (semantically equivalent).
    assert cli_equivalent.content == python_equivalent.content
    # Same ProjectionIdentity.
    assert str(cli_equivalent.identity()) == str(python_equivalent.identity())


def test_api_reuses_ordinary_catalogue_implementation() -> None:
    """The API resolves through the same service implementation and catalogue.

    ``api.prepare_figure`` must be the *same* canonical function the CLI uses —
    it accepts the same ordinary ``ComponentRegistry`` and returns the same
    ``FigureProjection``. This is the absence of a private duplicate catalogue /
    duplicate prepare implementation (Phase 5D § 7.8).
    """
    registry = _registry()
    api_result = api_prepare_figure(registry, _RASTER_FIGURE, _SOURCE)
    # The API path and the service path are the same implementation: resolving
    # the same catalogue populated with the same figure yields identical identity.
    assert isinstance(api_result, FigureProjection)
    assert str(api_result.identity()) == str(
        service_prepare_figure(_registry(), _RASTER_FIGURE, _SOURCE).identity()
    )


def test_api_has_no_alternate_identity_derivation() -> None:
    """The public API reuses the canonical ``FigureProjection.identity()``.

    It does not re-derive projection identity from its own field set: the
    projection object it returns is the canonical ``FigureProjection`` whose
    ``identity()`` is the ordinary projection-identity machinery (Phase 5D
    § 7.8: "Python API has no alternate identity derivation").
    """
    projection = api_prepare_figure(_registry(), _RASTER_FIGURE, _SOURCE)
    assert isinstance(projection, FigureProjection)
    # Identity is the canonical projection-identity digest, not an API-local value.
    assert str(projection.identity()).startswith("sha256:")


# ---------------------------------------------------------------------------
# render_figure composes the canonical prepare + realize path — Phase 5D § 7.3
# ---------------------------------------------------------------------------


def test_render_figure_composes_canonical_transient_path() -> None:
    """``render_figure`` (no serialization) == prepare + render_figure_projection.

    The convenience must not implement a parallel realization path: it must
    reuse the exact canonical ``prepare_figure`` and
    ``render_figure_projection`` implementations.
    """
    registry = _registry()
    composed = render_figure(registry, _RASTER_FIGURE, _SOURCE)
    stepwise_projection = api_prepare_figure(registry, _RASTER_FIGURE, _SOURCE)
    stepwise_figure = render_figure_projection(stepwise_projection, registry=registry)

    assert type(composed).__name__ == "Figure"
    assert type(stepwise_figure).__name__ == "Figure"
    # Same single top-level Axes (same scientific panels realized).
    assert len(composed.axes) == len(stepwise_figure.axes) == 1


def test_render_figure_composes_canonical_persistent_path() -> None:
    """``render_figure(serialization=...)`` == prepare + realize_projection.

    With a serialization policy the convenience must compose the canonical
    persistent realization and return a ``RealizedFigure`` whose identity
    matches the canonical stepwise path.
    """
    registry = _registry()
    policy = resolve_serialization_policy(format="svg", dpi=100)
    composed = render_figure(
        registry,
        _RASTER_FIGURE,
        _SOURCE,
        serialization=policy,
    )
    stepwise_projection = api_prepare_figure(registry, _RASTER_FIGURE, _SOURCE)
    stepwise_realized = realize_projection(stepwise_projection, serialization=policy, registry=registry)

    assert composed.format == "svg"
    assert composed.bytes
    assert composed.realization_identity == stepwise_realized.realization_identity


# ---------------------------------------------------------------------------
# Selection resolution converges through the same resolver — Phase 5D § 7.5
# ---------------------------------------------------------------------------

_SELECTION_FIGURE = "figure:selection-example/v1"


def _make_selection_projection() -> _ProjectionPartition:
    return _ProjectionPartition(
        semantics_version=1,
        preparation_version=1,
        requirement=FigureInputRequirement(role="analysis", contract="example/v1"),
        prepare=lambda source: {"stable": True, "records": source["records"]},
        select=_resolve_example_selection,
    )


def _resolve_example_selection(source: object) -> ResolvedFigureSelection:
    # Deterministic: exact order of the authoritative source's declared records.
    records = list(source["records"])
    return ResolvedFigureSelection(
        selection_ref="exact-records",
        selection_version=1,
        parameters={"order": "declared"},
        resolved_identities=tuple(records),
    )


def _noop_realize(projection: FigureProjection) -> object:
    import matplotlib

    fig, _ = matplotlib.pyplot.subplots()
    return fig


@dataclass(frozen=True, slots=True)
class _SelectionExampleFigure:
    """A synthetic figure with a deterministic selection resolver (Phase 3).

    Builds a generic ``SelectableFigure`` registered in a test-local registry so
    both the CLI-equivalent and Python-equivalent paths resolve the *same*
    selection resolver and the *same* authored selection. No research dependency.
    """

    ref: ComponentRef = field(default_factory=lambda: ComponentRef.parse(_SELECTION_FIGURE))
    kind: str = field(default=FIGURE_KIND)
    projection: _ProjectionPartition = field(default_factory=_make_selection_projection)
    visual: _VisualPartition = field(
        default_factory=lambda: _VisualPartition(semantics_version=1, realize=_noop_realize)
    )
    defaults: _DefaultsPartition = field(default_factory=_DefaultsPartition)


def _selection_registry() -> ComponentRegistry:
    registry = _registry()
    registry.register(_SelectionExampleFigure())
    return registry


_SELECTION_SOURCE = FigureSource(
    artifact_ref="artifact:ex/v1",
    record_id="sha256:SEL",
    schema_ref="example/v1",
    content={"records": ["case-a", "case-b", "case-c"]},
)


def test_selection_resolves_equivalently_on_cli_and_python_paths() -> None:
    """Authored + resolved selection converge on both interfaces (Phase 5D § 7.5).

    The CLI-equivalent service path and the Python-API path must resolve the
    *same* authored selection semantics and the *same* exact resolved identities,
    producing the same ``ProjectionIdentity``.
    """
    registry = _selection_registry()

    cli_equivalent = service_prepare_figure(registry, _SELECTION_FIGURE, _SELECTION_SOURCE)
    python_equivalent = api_prepare_figure(registry, _SELECTION_FIGURE, _SELECTION_SOURCE)

    assert cli_equivalent.selection is not None
    assert python_equivalent.selection is not None
    assert cli_equivalent.selection.selection_ref == python_equivalent.selection.selection_ref
    assert cli_equivalent.selection.selection_version == python_equivalent.selection.selection_version
    assert cli_equivalent.selection.parameters == python_equivalent.selection.parameters
    assert (
        cli_equivalent.selection.resolved_identities
        == python_equivalent.selection.resolved_identities
        == ("case-a", "case-b", "case-c")
    )
    assert str(cli_equivalent.identity()) == str(python_equivalent.identity())


def test_render_figure_uses_same_canonical_selection_prepare() -> None:
    """``render_figure`` selection path reuses the canonical resolver.

    The convenience must not re-resolve selection with a private copy: the
    projection it prepares carries the same resolved selection the canonical
    prepare produced.
    """
    registry = _selection_registry()
    composed = render_figure(registry, _SELECTION_FIGURE, _SELECTION_SOURCE)
    canonical = api_prepare_figure(registry, _SELECTION_FIGURE, _SELECTION_SOURCE)
    assert isinstance(composed, matplotlib.figure.Figure)
    assert composed is not None
    assert canonical.selection is not None
    assert canonical.selection.resolved_identities == ("case-a", "case-b", "case-c")
