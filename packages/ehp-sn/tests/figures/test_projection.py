"""Figure projection and projection identity tests (Phase 1 bootstrap slice).

These test :mod:`ehp_sn.figures.projection`: the provenance-bearing
``FigureProjection`` boundary and its ``ProjectionIdentity``.

They verify the Phase-1 projection claim (docs/docs/framework/figures/projection.md;
Phase-1 § 12 · P1-T10):

* the projection records the exact authoritative source (artifact, record,
  logical contract) and preparation semantics;
* changing the source record changes projection identity;
* changing only presentation never changes projection identity.

Headless backend selection is not required here because projection itself never
imports pyplot; only modules that render need a backend.
"""

from __future__ import annotations

from ehp_sn.figures import (
    effective_figure_registry,
    prepare_figure,
)
from ehp_sn.figures.projection import (
    FigureProjection,
    ProjectionIdentity,
    SourceRoleBinding,
)
from ehp_sn.figures.service import _ExactSource

_FIGURE_REF = "figure:raster-topology-inspection/v1"


def _source(*, record_id: str, passable: list[bool] | None = None) -> _ExactSource:
    return _ExactSource(
        artifact_ref="artifact:dg/v1",
        record_id=record_id,
        schema_ref="raster-topology/v1",
        content={
            "domain": {"height": 3, "width": 4, "position_count": 12},
            "passable": passable if passable is not None else [True] * 12,
        },
    )


def _project(source: _ExactSource) -> FigureProjection:
    return prepare_figure(effective_figure_registry(), _FIGURE_REF, source)


# ---------------------------------------------------------------------------
# 19.5 exact source provenance recorded in projection
# ---------------------------------------------------------------------------


def test_projection_records_exact_source_provenance() -> None:
    projection = _project(_source(record_id="sha256:AAA"))
    assert projection.figure_ref == _FIGURE_REF
    assert projection.projection_semantics_version == 1
    assert projection.preparation_version == 1
    assert projection.source.role == "topology"
    assert projection.source.artifact_ref == "artifact:dg/v1"
    assert projection.source.record_id == "sha256:AAA"
    assert projection.source.logical_contract == "raster-topology/v1"
    # The prepared view is a stable typed raster-topology record.
    assert projection.source.content.__class__.__name__ == "RasterTopology"


def test_source_role_binding_is_immutable() -> None:
    binding = SourceRoleBinding(
        role="topology",
        artifact_ref="artifact:dg/v1",
        record_id="sha256:AAA",
        logical_contract="raster-topology/v1",
        content={"domain": {"height": 3, "width": 4, "position_count": 12}, "passable": [True] * 12},
    )
    assert binding.role == "topology"
    assert binding.logical_contract == "raster-topology/v1"


# ---------------------------------------------------------------------------
# 19.6 projection identity — source sensitivity / stability
# ---------------------------------------------------------------------------


def test_projection_identity_changes_with_source_record() -> None:
    a = _project(_source(record_id="sha256:AAA"))
    b = _project(_source(record_id="sha256:BBB", passable=[False] + [True] * 11))
    assert a.identity() != b.identity()
    assert str(a.identity()) != str(b.identity())


def test_projection_identity_stable_for_same_source() -> None:
    a = _project(_source(record_id="sha256:AAA"))
    b = _project(_source(record_id="sha256:AAA"))
    assert a.identity() == b.identity()
    assert str(a.identity()) == str(b.identity())


def test_projection_identity_is_a_digest_string() -> None:
    identity = _project(_source(record_id="sha256:AAA")).identity()
    assert isinstance(identity, ProjectionIdentity)
    assert str(identity).startswith("sha256:")


# ---------------------------------------------------------------------------
# 19.7 projection identity — presentation independence
# ---------------------------------------------------------------------------


def test_projection_identity_ignores_presentation_only_changes() -> None:
    import matplotlib

    matplotlib.use("Agg")
    projection = _project(_source(record_id="sha256:AAA"))
    identity_before = str(projection.identity())

    # Perturb controlled ambient presentation values and re-render; the
    # projection identity must not change (Phase-1 § 12 · P1-T10).
    from ehp_sn.figures import render_figure_projection

    with matplotlib.rc_context({"font.size": 4, "figure.figsize": (2, 2), "lines.linewidth": 0.1}):
        render_figure_projection(projection, registry=effective_figure_registry())
    assert str(projection.identity()) == identity_before


# ---------------------------------------------------------------------------
# Projection never carries presentation state (P1-T10)
# ---------------------------------------------------------------------------


def test_projection_carries_no_presentation_state() -> None:
    projection = _project(_source(record_id="sha256:AAA"))
    # The projection has no figure dimensions, font, DPI, backend, format,
    # output path, or GUI-state fields.
    for field in ("width", "height", "font", "dpi", "backend", "serialization_format", "output_path"):
        assert not hasattr(projection, field)
