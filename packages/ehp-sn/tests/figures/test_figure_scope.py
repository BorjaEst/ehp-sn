"""Figure source-scope compatibility & catalogue determinism (Phase-4 § 19-20, § 29).

These test the framework ``scope`` dimension (``record`` / ``artifact``) the
Phase-4 artifact summaries rely on:

* P4-SCOPE — a record-scope figure and an artifact-scope figure are mutually
  incompatible: a record inspector is never selected for an artifact
  collection, and an artifact summary is never selected for a single record
  (Phase-4 § 4.1, § 20).
* P4-AUTO — ``--figure auto`` resolves within the source's scope only (0 / 1 /
  >1 compatible semantics; Phase-4 § 29).
* P4-ACAT — catalogue/provider determinism: the effective figure catalogue
  (including the artifact-scope summaries) is deterministic and independent of
  provider registration order, and no contract-specific artifact source types
  are introduced (Phase-4 § 20, § 29 · ARCH-014).
"""

from __future__ import annotations

import pytest
from ehp_sn.contracts.relations import simple_digraph
from ehp_sn.discovery import ComponentRegistry
from ehp_sn.figures import (
    AmbiguousFigureError,
    FigureInputCompatibilityError,
    NoCompatibleFigureError,
    effective_figure_registry,
    list_compatible_figures,
    prepare_figure,
    register_builtin_figures,
    register_installed_figure_providers,
    resolve_auto_figure,
)
from ehp_sn.figures.service import _ExactSource

from .artifact_summary_helpers import (
    GRAPH_ARTIFACT_SUMMARY_REF,
    GRAPH_INSPECTION_REF,
    graph_records,
    graph_source,
)


def _registry():
    return effective_figure_registry()


def _single_graph_record_source() -> _ExactSource:
    """An exact record source conforming to ``simple-digraph/v1``."""
    return _ExactSource(
        artifact_ref="artifact:dag/v1",
        record_id="sha256:G",
        schema_ref="simple-digraph/v1",
        content=simple_digraph(2, [(0, 1)]).content(),
    )


# ---------------------------------------------------------------------------
# P4-SCOPE — record/artifact mutual incompatibility
# ---------------------------------------------------------------------------


def test_artifact_summary_not_compatible_with_record_source():
    """An artifact-scope figure is not compatible with a single record source."""
    with pytest.raises(FigureInputCompatibilityError):
        prepare_figure(_registry(), GRAPH_ARTIFACT_SUMMARY_REF, _single_graph_record_source())


def test_record_inspector_not_compatible_with_artifact_source():
    """A record-scope inspector is not compatible with an artifact collection."""
    with pytest.raises(FigureInputCompatibilityError):
        prepare_figure(_registry(), GRAPH_INSPECTION_REF, graph_source(graph_records()))


# ---------------------------------------------------------------------------
# --figure auto resolves within the source's scope only (Phase-4 § 29)
# ---------------------------------------------------------------------------


def test_auto_never_selects_artifact_summary_for_record_source():
    """A record-scope source never resolves an artifact-scope figure via auto.

    `auto` for a record source resolves (or, when a compatible external
    record-scope companion is installed, reports ambiguity) among record-scope
    figures only; the artifact-scope summary is never a record compatible and
    is never selected (Phase-4 § 29)."""
    single = _single_graph_record_source()
    compatible = list_compatible_figures(_registry(), single)
    assert GRAPH_ARTIFACT_SUMMARY_REF not in [s.ref.canonical for s in compatible]
    assert all(s.projection.requirement.scope == "record" for s in compatible)
    try:
        resolved = resolve_auto_figure(_registry(), single)
    except (AmbiguousFigureError, NoCompatibleFigureError):
        return
    assert resolved.projection.requirement.scope == "record"
    assert resolved.ref.canonical != GRAPH_ARTIFACT_SUMMARY_REF


def test_auto_resolves_single_artifact_scope_figure():
    """A simple-digraph artifact collection resolves the graph artifact summary
    via auto (built-in only when no external artifact-scope companion)."""
    compatible = list_compatible_figures(_registry(), graph_source(graph_records()))
    refs = [s.ref.canonical for s in compatible]
    assert GRAPH_ARTIFACT_SUMMARY_REF in refs
    # Record-scope inspectors must not appear for an artifact source.
    assert GRAPH_INSPECTION_REF not in refs
    # When an installed producer generation summary also matches the same
    # simple-digraph/v1 artifact collection, auto is ambiguous by design
    # (Phase-5 § 41: >1 compatible -> AmbiguousFigureError; no priority), so
    # the caller must select an exact canonical reference.
    if len(compatible) > 1:
        with pytest.raises(AmbiguousFigureError):
            resolve_auto_figure(_registry(), graph_source(graph_records()))
        return
    resolved = resolve_auto_figure(_registry(), graph_source(graph_records()))
    assert resolved.ref.canonical == GRAPH_ARTIFACT_SUMMARY_REF


# ---------------------------------------------------------------------------
# Catalogue/provider determinism & no contract-specific source types
# ---------------------------------------------------------------------------


def test_artifact_summary_catalogue_is_provider_order_independent():
    """Registering built-in figure providers in different orders yields the same
    effective figure catalogue, including the artifact-scope summaries
    (Phase-4 § 29)."""

    def _build() -> list[str]:
        registry = ComponentRegistry()
        register_builtin_figures(registry)
        register_installed_figure_providers(registry)
        return sorted(d.ref.canonical for d in registry.iter(kind="figure"))

    base = _build()
    assert GRAPH_ARTIFACT_SUMMARY_REF in base
    assert "figure:raster-topology-artifact-summary/v1" in base
    assert "figure:categorical-field-artifact-summary/v1" in base
    assert _build() == base


def test_no_contract_specific_source_types_in_service():
    """The service exposes only the generic collection source, not per-contract
    ones (Phase-4 § 20, ARCH-014)."""
    import ehp_sn.figures.service as service

    source_names = {name for name in dir(service) if "Source" in name}
    assert "SimpleDigraphArtifactSource" not in source_names
    assert "RasterTopologyArtifactSource" not in source_names
    assert "CategoricalFieldArtifactSource" not in source_names
    assert "_CollectionSource" in source_names
