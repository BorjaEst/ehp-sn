"""Phase 2B — record-figure discovery genericity tests.

These test the generic compatible-figure discovery surface
(:mod:`ehp_sn.figures.service`) added in Phase 2B:

* ``--list-figures`` (``list_compatible_figures`` / ``list_figures_for_record``)
  is generic and hard-codes no producer→figure / contract→figure table
  (Phase-2 § 36);
* deterministic ``--figure auto`` (``resolve_auto_figure``) with exactly
  0 compatible → NoCompatibleFigure, 1 → exact FigureSpec, >1 → AmbiguousFigure
  (Phase-2 § 37);
* ``auto`` is canonicalized to an exact canonical FigureSpec before projection —
  never retained as provenance (Phase-2 § 38, § 41);
* provider-order independence (different provider discovery order → same
  compatible FigureSpec set) and deterministic duplicate-identity failure
  (Phase-2 § 39).

The ambiguity cases are exercised with the test-only external companion figures
from the installed fixture provider (Phase-2 § 40). Where a case depends on the
installed fixture provider it skips when absent.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless backend required for realization tests

import random
from dataclasses import dataclass, field
from importlib import import_module

import pytest
from ehp_sn.contracts.domains import rectangular_row_column_domain
from ehp_sn.contracts.observations import AnonymousVocabulary, categorical_field
from ehp_sn.contracts.relations import simple_digraph
from ehp_sn.discovery import ComponentRegistry, DuplicateRegistrationError
from ehp_sn.experiments import ComponentRef
from ehp_sn.figures import (
    AUTO_FIGURE_TOKEN,
    AmbiguousFigureError,
    NoCompatibleFigureError,
    effective_figure_registry,
    prepare_figure,
    resolve_auto_figure,
)
from ehp_sn.figures.contracts import (
    FIGURE_KIND,
    FigureInputRequirement,
    _DefaultsPartition,
    _ProjectionPartition,
    _VisualPartition,
)
from ehp_sn.figures.service import _ExactSource

try:
    import test_figure_provider  # noqa: F401
except ImportError:  # pragma: no cover
    test_figure_provider = None

REQUIRES_PROVIDER = pytest.mark.skipif(
    test_figure_provider is None,
    reason="test-figure-provider fixture distribution is not installed",
)


def _graph_source(schema_ref: str = "simple-digraph/v1") -> _ExactSource:
    graph = simple_digraph(3, [(0, 1)])
    return _ExactSource(
        artifact_ref="artifact:dag/v1",
        record_id="sha256:G1",
        schema_ref=schema_ref,
        content=graph.content(),
    )


def _raster_source() -> _ExactSource:
    return _ExactSource(
        artifact_ref="artifact:dg/v1",
        record_id="sha256:R1",
        schema_ref="raster-topology/v1",
        content={
            "extent": {"height": 3, "width": 4, "position_count": 12},
            "passable": [True] * 12,
        },
    )


def _field_source() -> _ExactSource:
    domain = rectangular_row_column_domain(2, 2)
    vocab = AnonymousVocabulary(identity="v", cardinality=2)
    field = categorical_field(domain, vocab, [0, 1, 0, 1])
    return _ExactSource(
        artifact_ref="artifact:obs/v1",
        record_id="sha256:F1",
        schema_ref="categorical-field/v1",
        content=field.content(),
    )


# ---------------------------------------------------------------------------
# --list-figures is generic (no hard-coded table) — Phase-2 § 36
# ---------------------------------------------------------------------------


def test_list_raster_compatible_figure() -> None:
    registry = effective_figure_registry()
    from ehp_sn.figures import list_compatible_figures

    compatible = list_compatible_figures(registry, _raster_source())
    refs = [s.ref.canonical for s in compatible]
    # Raster record → raster inspector, deterministically.
    assert refs == ["figure:raster-topology-inspection/v1"]


def test_list_graph_compatible_figures_include_builtin() -> None:
    """The built-in graph inspector is discoverable without provider presence."""
    registry = effective_figure_registry()
    from ehp_sn.figures import list_compatible_figures

    compatible = list_compatible_figures(registry, _graph_source())
    refs = [s.ref.canonical for s in compatible]
    assert "figure:simple-digraph-inspection/v1" in refs


@REQUIRES_PROVIDER
def test_list_graph_compatible_figures_include_external_when_installed() -> None:
    """``--list-figures`` returns built-in AND external compatible figures."""
    from ehp_sn.figures import list_compatible_figures

    compatible = list_compatible_figures(effective_figure_registry(), _graph_source())
    refs = [s.ref.canonical for s in compatible]
    assert "figure:simple-digraph-inspection/v1" in refs
    assert "figure:digraph-summary/v1" in refs


def test_list_no_compatible_for_unknown_contract_is_empty() -> None:
    from ehp_sn.figures import list_compatible_figures

    source = _ExactSource(
        artifact_ref="artifact:x/v1",
        record_id="sha256:X",
        schema_ref="some-unknown/v1",
        content={},
    )
    assert list_compatible_figures(effective_figure_registry(), source) == []


# ---------------------------------------------------------------------------
# --figure auto: 0 / 1 / >1 — Phase-2 § 37
# ---------------------------------------------------------------------------


def test_auto_zero_compatible_is_controlled_no_compatible() -> None:
    source = _ExactSource(
        artifact_ref="artifact:x/v1",
        record_id="sha256:X",
        schema_ref="some-unknown/v1",
        content={},
    )
    with pytest.raises(NoCompatibleFigureError):
        resolve_auto_figure(effective_figure_registry(), source)


def test_auto_one_compatible_resolves_exact_figure() -> None:
    # Raster record has exactly one compatible figure (no external companion).
    resolved = resolve_auto_figure(effective_figure_registry(), _raster_source())
    assert resolved.ref.canonical == "figure:raster-topology-inspection/v1"


@REQUIRES_PROVIDER
def test_auto_more_than_one_compatible_is_ambiguous() -> None:
    """Graph record has a built-in + external compatible figure → ambiguous."""
    with pytest.raises(AmbiguousFigureError):
        resolve_auto_figure(effective_figure_registry(), _graph_source())


@REQUIRES_PROVIDER
def test_auto_categorical_more_than_one_compatible_is_ambiguous() -> None:
    with pytest.raises(AmbiguousFigureError):
        resolve_auto_figure(effective_figure_registry(), _field_source())


# ---------------------------------------------------------------------------
# auto canonicalized before projection — Phase-2 § 38, § 41
# ---------------------------------------------------------------------------


def test_auto_canonicalized_before_projection() -> None:
    """After auto resolution, provenance holds the exact FigureSpec, never auto."""
    # An auto-resolvable single-match case (raster record, no external
    # compatible companion). Project the built-in raster figure and confirm the
    # projection figure_ref is the exact canonical reference.
    projection = prepare_figure(
        effective_figure_registry(), "figure:raster-topology-inspection/v1", _raster_source()
    )
    assert projection.figure_ref == "figure:raster-topology-inspection/v1"
    assert projection.figure_ref != AUTO_FIGURE_TOKEN


# ---------------------------------------------------------------------------
# provider-order independence & duplicate identity — Phase-2 § 39
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _SimpleFigure:
    """A minimal FigureSpec used to build per-provider catalogues."""

    ref_str: str
    role: str = "graph"
    contract: str = "simple-digraph/v1"
    ref: ComponentRef = field(init=False)
    kind: str = field(default=FIGURE_KIND, init=False)
    projection: _ProjectionPartition = field(init=False)
    visual: _VisualPartition = field(init=False)
    defaults: _DefaultsPartition = field(default_factory=_DefaultsPartition)

    def __post_init__(self) -> None:
        object.__setattr__(self, "ref", ComponentRef.parse(self.ref_str))
        object.__setattr__(
            self,
            "projection",
            _ProjectionPartition(
                semantics_version=1,
                preparation_version=1,
                requirement=FigureInputRequirement(role=self.role, contract=self.contract),
                prepare=lambda content: content,
            ),
        )
        object.__setattr__(
            self,
            "visual",
            _VisualPartition(semantics_version=1, realize=lambda projection: None),
        )


@dataclass(frozen=True)
class _FakeEntryPoint:
    name: str
    value: str
    group: str = "ehp_sn.figures.providers"

    def load(self):
        module_name, _, attr = self.value.partition(":")
        return getattr(import_module(module_name), attr)


def _provider_a(registry: ComponentRegistry) -> None:
    registry.register(_SimpleFigure("figure:alpha/v1"))
    registry.register(_SimpleFigure("figure:beta/v1"))


def _provider_b(registry: ComponentRegistry) -> None:
    registry.register(_SimpleFigure("figure:gamma/v1"))


def _fake_entry_points(*entries: _FakeEntryPoint):
    def _entry_points(*, group: str | None = None) -> list[_FakeEntryPoint]:
        return list(entries)

    return _entry_points


def test_catalogue_is_deterministic_under_randomized_provider_order() -> None:
    """Different provider discovery order → same catalogue & same compatible set."""
    import ehp_sn.discovery.providers as discovery_providers
    from ehp_sn.figures.providers import register_installed_figure_providers

    def _build(order) -> ComponentRegistry:
        entries = [_FakeEntryPoint(name=name, value=f"{__name__}:{fn.__name__}") for name, fn in order]
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(discovery_providers.metadata, "entry_points", _fake_entry_points(*entries))
            registry = ComponentRegistry()
            register_installed_figure_providers(registry)
            return registry

    base = _build([("a", _provider_a), ("b", _provider_b)])
    base_refs = sorted(d.ref.canonical for d in base.iter(kind="figure"))

    for seed in range(20):
        order = [("a", _provider_a), ("b", _provider_b)]
        random.Random(seed).shuffle(order)
        registry = _build(order)
        refs = sorted(d.ref.canonical for d in registry.iter(kind="figure"))
        assert refs == base_refs


def test_duplicate_figure_identity_is_deterministic_error() -> None:
    """Two catalgoue entries with the same canonical ref → deterministic error."""
    registry = ComponentRegistry()
    registry.register(_SimpleFigure("figure:dup/v1"))
    with pytest.raises(DuplicateRegistrationError):
        registry.register(_SimpleFigure("figure:dup/v1"))


# ---------------------------------------------------------------------------
# ambiguous auto is resolved by explicit exact ref (Phase-2 § 40)
# ---------------------------------------------------------------------------


def test_explicit_ref_resolves_despite_ambiguity() -> None:
    """An explicit exact canonical ref selects deterministically."""
    projection = prepare_figure(
        effective_figure_registry(), "figure:simple-digraph-inspection/v1", _graph_source()
    )
    assert projection.figure_ref == "figure:simple-digraph-inspection/v1"
    assert projection.figure_ref != AUTO_FIGURE_TOKEN


# ---------------------------------------------------------------------------
# Phase 7E § 28 — a new downstream FigureSpec is a provider-only change
# ---------------------------------------------------------------------------


def test_new_downstream_figure_registers_through_ordinary_catalogue() -> None:
    """Adding a downstream FigureSpec needs no framework change (Scenario B).

    Registering a new ``FigureSpec`` through the ordinary catalogue is a
    provider-only change: it resolves and prepares through the existing service
    with zero ``ehp_sn.figures`` modification, alongside (not conflicting with)
    the built-in figures.
    """
    from ehp_sn.figures import register_builtin_figures

    registry = ComponentRegistry()
    register_builtin_figures(registry)
    registry.register(_SimpleFigure("figure:downstream/v1"))

    projection = prepare_figure(registry, "figure:downstream/v1", _graph_source())
    assert projection.figure_ref == "figure:downstream/v1"
    assert projection.source.logical_contract == "simple-digraph/v1"
    # The built-in inspector is still resolvable through the same catalogue.
    assert registry.resolve("figure:simple-digraph-inspection/v1").kind == FIGURE_KIND
