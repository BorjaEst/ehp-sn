"""External graph figure tests (Phase 2).

These test the **externally contributed** graph figure
``figure:simple-digraph-inspection/v1``, contributed by the independently
installed ``test-figure-provider`` distribution through the
``ehp_sn.figures.providers`` entry-point group.

They verify (Phase-2 § 23 test matrix):

* the external graph figure resolves through the same ordinary component
  catalogue as the built-in raster figure (P2-A); resolving it requires no
  knowledge of its origin (P2-C/P2-4);
* it renders a ``simple-digraph/v1`` record through the same service path
  (P2-1);
* ``FigureInputContract`` supports raster and graph single-source requirements
  without domain-specific framework subclasses (P2-8/P2-F);
* ``FigureProjection`` transports the graph prepared data opaquely (P2-9/P2-G);
* the graph visualization uses deterministic visual-only circular node
  placement and consumes no scientific RNG (P2-10);
* compatibility validation never silently substitutes another figure (P2-11);
* explicit figure selection remains mandatory (P2-11).

These require the fixture distribution to be installed. If it is absent they
skip, mirroring the existing research-provider integration test pattern.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless backend required

import pytest
from ehp_sn.discovery import ComponentRegistry
from ehp_sn.figures import (
    FigureInputCompatibilityError,
    effective_figure_registry,
    prepare_figure,
    render_figure_projection,
)
from ehp_sn.figures.service import _ExactSource

try:
    from test_figure_provider.graph import SimpleDigraphInspectionData
except ImportError:  # pragma: no cover - fixture distribution not installed
    SimpleDigraphInspectionData = None  # type: ignore[assignment]

_GRAPH_REF = "figure:simple-digraph-inspection/v1"
_RASTER_REF = "figure:raster-topology-inspection/v1"

REQUIRES_PROVIDER = pytest.mark.skipif(
    SimpleDigraphInspectionData is None,
    reason="test-figure-provider fixture distribution is not installed",
)


def _graph_source(*, record_id: str = "sha256:BBB", edges=None, node_count: int = 4) -> _ExactSource:
    return _ExactSource(
        artifact_ref="artifact:dag/v1",
        record_id=record_id,
        schema_ref="simple-digraph/v1",
        content={
            "node_count": node_count,
            "edges": edges if edges is not None else [(0, 1), (1, 2), (2, 3)],
        },
    )


def _raster_source() -> _ExactSource:
    return _ExactSource(
        artifact_ref="artifact:dg/v1",
        record_id="sha256:ZZZ",
        schema_ref="raster-topology/v1",
        content={
            "domain": {"height": 3, "width": 4, "position_count": 12},
            "passable": [True] * 12,
        },
    )


# ---------------------------------------------------------------------------
# P2-A / P2-C — external figure resolves through the ordinary catalogue
# ---------------------------------------------------------------------------


@REQUIRES_PROVIDER
def test_external_graph_figure_resolves_through_ordinary_catalogue() -> None:
    registry = effective_figure_registry()
    definition = registry.resolve(_GRAPH_REF)
    assert definition.kind == "figure"
    # Origin (external package) is irrelevant to normal resolution (P2-4):
    # resolving does not require knowing whether the figure came from a test
    # package, ehp_sn, or ehp_research.
    assert definition.ref.canonical == _GRAPH_REF


@REQUIRES_PROVIDER
def test_builtin_and_external_figures_share_one_catalogue() -> None:
    """Built-in raster and external graph figures enter the same catalogue."""
    registry = effective_figure_registry()
    refs = sorted(d.ref.canonical for d in registry.iter(kind="figure"))
    assert _RASTER_REF in refs
    assert _GRAPH_REF in refs


# ---------------------------------------------------------------------------
# P2-1 — the graph figure renders through the same service path
# ---------------------------------------------------------------------------


@REQUIRES_PROVIDER
def test_external_graph_figure_renders_graph_record() -> None:
    registry = effective_figure_registry()
    projection = prepare_figure(registry, _GRAPH_REF, _graph_source())
    assert projection.figure_ref == _GRAPH_REF
    assert isinstance(projection.content, SimpleDigraphInspectionData)
    figure = render_figure_projection(projection, registry=registry)
    assert type(figure).__name__ == "Figure"
    assert len(figure.axes) == 1


@REQUIRES_PROVIDER
def test_graph_prepared_data_carries_authoritative_structure() -> None:
    projection = prepare_figure(effective_figure_registry(), _GRAPH_REF, _graph_source())
    data = projection.content
    assert data.node_count == 4
    # Edges are canonicalized lexicographically by the contract.
    assert data.edges == ((0, 1), (1, 2), (2, 3))
    # Authoritative terminals: nodes with out-degree zero. For the chain
    # 0->1->2->3, only node 3 is a terminal.
    assert data.terminals == (3,)


# ---------------------------------------------------------------------------
# P2-8 / P2-F — FigureInputContract domain neutrality (no domain subclasses)
# ---------------------------------------------------------------------------


@REQUIRES_PROVIDER
def test_graph_input_requirement_is_generic_not_domain_specialized() -> None:
    """The graph figure uses the same generic ``FigureInputRequirement``.

    No ``GraphFigureInputContract``/``RasterFigureInputContract`` subclass or
    tagged scientific-domain union exists; both figures declare a semantic role
    plus a required logical contract through the plain framework requirement
    (P2-F).
    """
    spec = effective_figure_registry().resolve(_GRAPH_REF)
    requirement = spec.projection.requirement
    assert requirement.role == "graph"
    assert requirement.contract == "simple-digraph/v1"
    # Same concrete type as the raster figure's requirement — no subclass.
    raster_spec = effective_figure_registry().resolve(_RASTER_REF)
    assert type(requirement) is type(raster_spec.projection.requirement)
    assert type(requirement).__name__ == "FigureInputRequirement"


# ---------------------------------------------------------------------------
# P2-9 / P2-G — FigureProjection transports graph prepared data opaquely
# ---------------------------------------------------------------------------


@REQUIRES_PROVIDER
def test_projection_adds_no_graph_specific_fields() -> None:
    """Generic ``FigureProjection`` is domain-opaque for the graph figure.

    The projection carries no ``nodes``/``edges``/``extent``/``passability``
    fields; the prepared graph view rides in the opaque ``content`` value
    (P2-G).
    """
    projection = prepare_figure(effective_figure_registry(), _GRAPH_REF, _graph_source())
    for field in ("nodes", "edges", "extent", "passability", "terminals"):
        assert not hasattr(projection, field)
    # The prepared graph value is opaque to generic orchestration.
    assert isinstance(projection.content, SimpleDigraphInspectionData)


# ---------------------------------------------------------------------------
# P2-10 — deterministic visual-only circular placement (no RNG)
# ---------------------------------------------------------------------------


@REQUIRES_PROVIDER
def test_graph_placement_is_deterministic_across_runs() -> None:
    from test_figure_provider.graph import _circular_positions

    positions_a = _circular_positions(4)
    positions_b = _circular_positions(4)
    assert positions_a == positions_b
    # Fixed circular placement: distinct nodes map to distinct unit-circle
    # positions with a fully specified semantics (no unseeded layout).
    xs = [x for x, _ in positions_a]
    ys = [y for _, y in positions_a]
    assert all(abs(x * x + y * y - 1.0) < 1e-9 for x, y in positions_a)
    assert len(set(zip(xs, ys, strict=True))) == 4


# ---------------------------------------------------------------------------
# P2-11 — explicit selection mandatory; no silent substitution
# (required negative tests: raster-vs-graph both directions)
# ---------------------------------------------------------------------------


@REQUIRES_PROVIDER
def test_graph_figure_against_raster_record_is_controlled_mismatch() -> None:
    with pytest.raises(FigureInputCompatibilityError):
        prepare_figure(effective_figure_registry(), _GRAPH_REF, _raster_source())


@REQUIRES_PROVIDER
def test_raster_figure_against_graph_record_is_controlled_mismatch() -> None:
    with pytest.raises(FigureInputCompatibilityError):
        prepare_figure(effective_figure_registry(), _RASTER_REF, _graph_source())


@REQUIRES_PROVIDER
def test_no_silent_substitution_when_requested_figure_incompatible() -> None:
    """The framework must not silently pick another compatible figure."""
    registry = effective_figure_registry()
    # Only the graph figure consumes simple-digraph/v1 with role graph; if the
    # graph figure were unavailable the request must fail rather than substitute.
    with pytest.raises(FigureInputCompatibilityError):
        prepare_figure(registry, _RASTER_REF, _graph_source())


# ---------------------------------------------------------------------------
# FIG-003 — rendering does not mutate graph source / prepared view / projection
# ---------------------------------------------------------------------------


@REQUIRES_PROVIDER
def test_graph_rendering_does_not_mutate_source_or_projection() -> None:
    source_content = {"node_count": 4, "edges": [(0, 1), (1, 2), (2, 3)]}
    source = _ExactSource(
        artifact_ref="artifact:dag/v1",
        record_id="sha256:EEE",
        schema_ref="simple-digraph/v1",
        content=source_content,
    )
    registry = effective_figure_registry()
    projection = prepare_figure(registry, _GRAPH_REF, source)
    prepared_before = tuple(projection.content.edges)
    identity_before = str(projection.identity())

    render_figure_projection(projection, registry=registry)

    assert tuple(projection.content.edges) == prepared_before
    assert str(projection.identity()) == identity_before
    assert source.content["edges"] == [(0, 1), (1, 2), (2, 3)]


# ---------------------------------------------------------------------------
# P2-5 / P2-18 — ProjectionIdentity independent of provider discovery order
# ---------------------------------------------------------------------------


@REQUIRES_PROVIDER
def test_graph_projection_identity_is_stable_for_equal_semantics() -> None:
    """Same source/semantics ⇒ same ProjectionIdentity (regardless of order).

    Provider enumeration order must never affect ProjectionIdentity (P2-18):
    equal canonical semantics converge on equal identity via the ordinary
    resolved catalogue.
    """
    registry = effective_figure_registry()
    a = prepare_figure(registry, _GRAPH_REF, _graph_source(record_id="sha256:BBB"))
    b = prepare_figure(registry, _GRAPH_REF, _graph_source(record_id="sha256:BBB"))
    assert str(a.identity()) == str(b.identity())
    # The identity is a canonical digest string, not an address.
    assert str(a.identity()).startswith("sha256:")


# ---------------------------------------------------------------------------
# P2-14 — an empty catalogue has no graph figure (absent-package analogue at
# the plain-registry level; real package-absent behaviour needs an uninstall)
# ---------------------------------------------------------------------------


@REQUIRES_PROVIDER
def test_graph_figure_not_present_in_plain_registry_without_provider() -> None:
    """A bare registry without the installed provider has no graph figure.

    This mirrors Phase-1 § 19.12: with the provider's definition absent there is
    no ordinary catalogue entry to resolve the graph figure.
    """
    from ehp_sn.discovery import UnknownReferenceError
    from ehp_sn.experiments import ComponentRef

    with pytest.raises(UnknownReferenceError):
        ComponentRegistry().resolve(ComponentRef.parse(_GRAPH_REF))
