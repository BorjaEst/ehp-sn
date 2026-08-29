"""Realization boundary, identity, lifecycle, and mutation tests.

These test :mod:`ehp_sn.figures.realization` (and the transient
``render_figure_projection`` path in :mod:`ehp_sn.figures.service`). They
validate the Phase-4 realization boundary
(``docs/docs/architecture/figures.md`` § "Phase 4"; ``rendering.md``):

* P4-1 — an existing ``FigureProjection`` is realized without rerunning
  scientific selection or preparation;
* P4-2 — one projection produces multiple independently identifiable
  realizations;
* P4-3 — ``ProjectionIdentity`` is invariant under presentation / serialization /
  realization-only changes;
* P4-4 — ``RealizationIdentity`` changes for presentation and serialization
  changes (and for a projection change);
* P4-6 — ``RenderingEnvironmentProvenance`` and ``ContentDigest`` remain
  separate from semantic ``RealizationIdentity``;
* P4-8 — at least one raster (PNG) and one vector (SVG) realization exist;
* P4-9 — framework-owned persistent Matplotlib figures have deterministic
  lifetime/cleanup (no leak) while the interactive path transfers ownership;
* Phase-4 § 18 modifiability and § 19 mutation claims.

It also closes the Phase-4 realization targets that make those concepts
**executable rather than merely present**:

* P4-T9  — one canonical resolved realization request, from which both identity
  and rendering inputs derive;
* P4-T10 — effective-presentation identity closure;
* P4-T14 — transient (interactive) realization identity semantics;
* P4-T16 — failure-path cleanup and rc-state restoration;
* P4-T17 — rendering-environment provenance adequacy;
* P4-T18 — semantic versus byte determinism contract.

Headless backend is required (``matplotlib.use("Agg")``).
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless backend required

import matplotlib.pyplot as plt
import pytest
from ehp_sn.digests import sha256_bytes_digest
from ehp_sn.figures import (
    RenderProfile,
    ResolvedFigureRealization,
    effective_figure_registry,
    prepare_figure,
    realize_projection,
    render_figure_projection,
    resolve_figure_realization,
    resolve_serialization_policy,
)
from ehp_sn.figures.service import _ExactSource

_FIGURE_REF = "figure:raster-topology-inspection/v1"


def _source(*, record_id: str = "sha256:AAA", passable=None) -> _ExactSource:
    if passable is None:
        passable = [True] * 12
    return _ExactSource(
        artifact_ref="artifact:dg/v1",
        record_id=record_id,
        schema_ref="raster-topology/v1",
        content={
            "domain": {"height": 3, "width": 4, "position_count": 12},
            "passable": passable,
        },
    )


def _projection(*, record_id: str = "sha256:AAA", passable=None, registry=None):
    reg = registry if registry is not None else effective_figure_registry()
    return prepare_figure(reg, _FIGURE_REF, _source(record_id=record_id, passable=passable))


def _png_policy(**kw):
    return resolve_serialization_policy(format="png", **kw)


def _svg_policy(**kw):
    return resolve_serialization_policy(format="svg", **kw)


# ---------------------------------------------------------------------------
# P4-1 — realization reuses an existing projection without rerunning prep
# ---------------------------------------------------------------------------


def test_realization_reuses_projection_without_repreparing() -> None:
    """Realization receives an already-prepared projection and never re-prepares.

    The projection is prepared once; realizing it any number of times must not
    call ``prepare`` again. The framework passes the same projection to the
    visual path, and the projection itself is unchanged after realization.
    """
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    prepared_identity = id(projection.content)

    r1 = realize_projection(projection, serialization=_png_policy(), registry=reg)
    r2 = realize_projection(projection, serialization=_svg_policy(), registry=reg)

    # Same projection instance produced both realizations (no re-resolution of a
    # fresh source), and the projection was not mutated.
    assert id(projection.content) == prepared_identity
    assert str(projection.identity()) == str(_projection(registry=reg).identity())
    # Both realizations reference the same projection identity.
    assert str(r1.realization_identity.projection_identity) == str(
        r2.realization_identity.projection_identity
    )
    assert str(r1.realization_identity.projection_identity) == str(projection.identity())


# ---------------------------------------------------------------------------
# P4-2 — one projection → multiple independently identifiable realizations
# ---------------------------------------------------------------------------


def test_one_projection_produces_multiple_independently_identifiable_realizations() -> None:
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    png = realize_projection(projection, serialization=_png_policy(), registry=reg)
    svg = realize_projection(projection, serialization=_svg_policy(), registry=reg)
    pub = realize_projection(
        projection,
        serialization=_png_policy(),
        presentation=RenderProfile(name="publication", version=1, width_inches=10, height_inches=6),
        registry=reg,
    )
    ids = {
        str(png.realization_identity),
        str(svg.realization_identity),
        str(pub.realization_identity),
    }
    assert len(ids) == 3  # three distinct realizations from one projection
    # All share the same projection identity.
    proj_ids = {
        str(png.realization_identity.projection_identity),
        str(svg.realization_identity.projection_identity),
        str(pub.realization_identity.projection_identity),
    }
    assert len(proj_ids) == 1


# ---------------------------------------------------------------------------
# P4-3 — ProjectionIdentity invariant under realization-only changes
# ---------------------------------------------------------------------------


def test_projection_identity_invariant_under_presentation_and_serialization() -> None:
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    base = str(projection.identity())

    # PNG / SVG serialization only.
    realize_projection(projection, serialization=_png_policy(), registry=reg)
    realize_projection(projection, serialization=_svg_policy(), registry=reg)
    assert str(projection.identity()) == base
    # Different presentation policies.
    for name, w, h in (("inspection", 6, 6), ("publication", 12, 8), ("compact", 4, 4)):
        realize_projection(
            projection,
            serialization=_png_policy(),
            presentation=RenderProfile(name=name, version=1, width_inches=w, height_inches=h),
            registry=reg,
        )
        assert str(projection.identity()) == base
    # DPI change.
    realize_projection(projection, serialization=_png_policy(dpi=200), registry=reg)
    assert str(projection.identity()) == base


def test_projection_change_changes_projection_and_realization_identity() -> None:
    reg = effective_figure_registry()
    a = _projection(record_id="sha256:AAA", registry=reg)
    b = _projection(record_id="sha256:BBB", passable=[False] + [True] * 11, registry=reg)
    assert str(a.identity()) != str(b.identity())
    ra = realize_projection(a, serialization=_png_policy(), registry=reg)
    rb = realize_projection(b, serialization=_png_policy(), registry=reg)
    assert str(ra.realization_identity) != str(rb.realization_identity)


# ---------------------------------------------------------------------------
# P4-4 — RealizationIdentity changes for relevant realization changes
# ---------------------------------------------------------------------------


def test_realization_identity_changes_with_serialization_format() -> None:
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    png = realize_projection(projection, serialization=_png_policy(), registry=reg)
    svg = realize_projection(projection, serialization=_svg_policy(), registry=reg)
    assert str(png.realization_identity) != str(svg.realization_identity)
    assert str(png.realization_identity.projection_identity) == str(
        svg.realization_identity.projection_identity
    )


def test_realization_identity_changes_with_serialization_parameter() -> None:
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    a = realize_projection(projection, serialization=_png_policy(dpi=100), registry=reg)
    b = realize_projection(projection, serialization=_png_policy(dpi=300), registry=reg)
    assert str(a.realization_identity) != str(b.realization_identity)
    assert str(a.realization_identity.projection_identity) == str(
        b.realization_identity.projection_identity
    )


def test_realization_identity_changes_with_presentation_policy() -> None:
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    a = realize_projection(projection, serialization=_png_policy(), registry=reg)
    b = realize_projection(
        projection,
        serialization=_png_policy(),
        presentation=RenderProfile(name="publication", version=1, width_inches=12, height_inches=8),
        registry=reg,
    )
    assert str(a.realization_identity) != str(b.realization_identity)
    assert str(a.realization_identity.projection_identity) == str(
        b.realization_identity.projection_identity
    )


def test_destination_is_not_part_of_realization_identity() -> None:
    """Changing only destination/placement must not change RealizationIdentity.

    ``RealizedFigure`` carries no destination/path field, so realization
    identity is defined without it (rendering.md § ``RealizationIdentity``;
    Phase-4 § 5).
    """
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    r = realize_projection(projection, serialization=_png_policy(), registry=reg)
    for field in ("destination", "output_path", "path", "artifact_dir", "report_section"):
        assert not hasattr(r, field)
        assert not hasattr(r.realization_identity, field)


# ---------------------------------------------------------------------------
# P4-6 — environment provenance and content digest separate from identity
# ---------------------------------------------------------------------------


def test_content_digest_and_provenance_are_distinct_from_realization_identity() -> None:
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    r = realize_projection(projection, serialization=_png_policy(), registry=reg)
    # Separate attributes, not merged into the identity.
    assert r.content_digest.value.startswith("sha256:")
    assert isinstance(r.environment.matplotlib_version, str)
    assert r.environment.backend
    assert str(r.realization_identity) != r.content_digest.value


def test_same_realization_identity_with_reproducible_bytes() -> None:
    """The identity is semantic; the digest is byte-level.

    Two realizations under the same environment reproduce the same serialized
    bytes (deterministic) and the same identity, while the content digest tracks
    the exact bytes. The model keeps semantic identity and byte integrity
    separate inputs.
    """
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    r1 = realize_projection(projection, serialization=_png_policy(), registry=reg)
    r2 = realize_projection(projection, serialization=_png_policy(), registry=reg)
    assert str(r1.realization_identity) == str(r2.realization_identity)
    assert r1.bytes == r2.bytes
    assert r1.content_digest.value == r2.content_digest.value


# ---------------------------------------------------------------------------
# P4-7 / P4-8 — serialization through the framework path; raster and vector
# ---------------------------------------------------------------------------


def test_serialization_occurs_through_framework_path() -> None:
    """The high-level realize path returns serialized bytes, not just a figure."""
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    r = realize_projection(projection, serialization=_png_policy(), registry=reg)
    assert isinstance(r.bytes, bytes)
    assert len(r.bytes) > 0
    assert r.format == "png"


def test_raster_and_vector_realizations() -> None:
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    png = realize_projection(projection, serialization=_png_policy(), registry=reg)
    svg = realize_projection(projection, serialization=_svg_policy(), registry=reg)
    assert png.format == "png"
    assert svg.format == "svg"
    assert png.bytes != svg.bytes
    # PNG is a raster format (starts with PNG signature), SVG is textual XML.
    assert png.bytes[:8] == b"\x89PNG\r\n\x1a\n"
    assert b"<svg" in svg.bytes


# ---------------------------------------------------------------------------
# P4-9 — framework-owned persistent figures have deterministic lifecycle
# ---------------------------------------------------------------------------


def test_persistent_realization_does_not_leak_matplotlib_figures() -> None:
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    baseline = len(plt.get_fignums())
    for _ in range(25):
        realize_projection(projection, serialization=_png_policy(), registry=reg)
    assert len(plt.get_fignums()) == baseline


def test_interactive_path_transfers_figure_ownership() -> None:
    """The interactive path returns a live Figure owned by the caller (P4-T8)."""
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    figure = render_figure_projection(projection, registry=reg)
    assert type(figure).__name__ == "Figure"
    assert len(figure.axes) == 1
    plt.close(figure)  # caller owns and closes it


# ---------------------------------------------------------------------------
# Phase-4 § 19 — realization does not mutate projection or source
# ---------------------------------------------------------------------------


def test_realization_does_not_mutate_projection_or_source() -> None:
    reg = effective_figure_registry()
    source_content = {
        "domain": {"height": 3, "width": 4, "position_count": 12},
        "passable": [True] * 12,
    }
    source = _ExactSource(
        artifact_ref="artifact:dg/v1",
        record_id="sha256:AAA",
        schema_ref="raster-topology/v1",
        content=source_content,
    )
    projection = prepare_figure(reg, _FIGURE_REF, source)
    prepared_before = tuple(projection.source.content.passable)
    identity_before = str(projection.identity())
    realize_projection(projection, serialization=_png_policy(), registry=reg)
    realize_projection(projection, serialization=_svg_policy(), registry=reg)
    assert tuple(projection.source.content.passable) == prepared_before
    assert str(projection.identity()) == identity_before
    assert source.content["passable"] == [True] * 12


# ---------------------------------------------------------------------------
# Phase-4 § 18 — modifiability: adding a format touches no projection/prep
# ---------------------------------------------------------------------------


def test_modifiable_add_format_touches_no_projection_or_prep() -> None:
    """Adding a serialization format must not change projection/preparation code.

    The framework realization path serializes generically by explicit format; the
    projection and prepared-data handling are format-independent. We verify the
    projection/preparation modules contain no serialization-format branching.
    """
    import pathlib

    from ehp_sn.figures import projection as projection_module

    proj_source = pathlib.Path(projection_module.__file__).read_text(encoding="utf-8")
    assert "png" not in proj_source
    assert "svg" not in proj_source
    assert "dpi" not in proj_source


# ---------------------------------------------------------------------------
# P4-T9 — one canonical resolved realization request
# ---------------------------------------------------------------------------


def test_resolve_figure_realization_is_single_source_for_identity_and_rc() -> None:
    """Identity and rendering inputs derive from the same resolved state.

    ``ResolvedFigureRealization`` is the one internal boundary between authored
    intent and Matplotlib. Realizing the same projection resolves to the same
    identity, and its effective rc is exactly what rendering consumes
    (P4-T9). No second resolution occurs inside serialization.
    """
    reg = effective_figure_registry()
    projection = _projection(registry=reg)

    resolved = resolve_figure_realization(projection, serialization=_png_policy(), registry=reg)
    assert isinstance(resolved, ResolvedFigureRealization)
    assert resolved.projection is projection  # same already-fixed projection
    assert "figure.figsize" in resolved.to_rc_params()
    # Re-resolving the same authored inputs reproduces the same identity.
    again = resolve_figure_realization(projection, serialization=_png_policy(), registry=reg)
    assert str(resolved.realization_identity()) == str(again.realization_identity())


def test_resolve_change_effective_width_changes_realization_identity() -> None:
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    base = resolve_figure_realization(projection, serialization=_png_policy(), registry=reg)
    wider = resolve_figure_realization(
        projection,
        serialization=_png_policy(),
        presentation=RenderProfile(name="pub", version=1, width_inches=12, height_inches=8),
        registry=reg,
    )
    assert str(base.realization_identity()) != str(wider.realization_identity())
    assert str(projection.identity()) == str(_projection(registry=reg).identity())


def test_resolve_change_effective_typography_changes_realization_identity() -> None:
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    base = resolve_figure_realization(projection, serialization=_png_policy(), registry=reg)
    with_font = resolve_figure_realization(
        projection,
        serialization=_png_policy(),
        presentation=RenderProfile(
            name="font", version=1, width_inches=6, height_inches=6, font_size=18
        ),
        registry=reg,
    )
    assert str(base.realization_identity()) != str(with_font.realization_identity())
    assert str(projection.identity()) == str(_projection(registry=reg).identity())


def test_resolve_layout_binding_placeholders_removed() -> None:
    """Speculative layout/binding placeholders must not appear (P4-T20).

    ``RealizationIdentity`` consumes only implemented semantics; no
    ``layout_identity`` / ``panel_binding_identity`` placeholder is present.
    """
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    resolved = resolve_figure_realization(projection, serialization=_png_policy(), registry=reg)
    identity = resolved.realization_identity()
    for attr in ("layout_identity", "panel_binding_identity"):
        assert not hasattr(identity, attr)


# ---------------------------------------------------------------------------
# P4-T10 — effective-presentation identity closure
# ---------------------------------------------------------------------------


def test_ambient_rcparams_do_not_change_identity() -> None:
    """Ambient (unresolved) rcParams are never part of effective presentation.

    Changing ambient Matplotlib state outside the framework's resolved
    presentation must not change realization identity (P4-T10).
    """
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    base = resolve_figure_realization(projection, serialization=_png_policy(), registry=reg)
    import matplotlib

    with matplotlib.rc_context({"font.size": 4, "lines.linewidth": 0.1}):
        inside = resolve_figure_realization(projection, serialization=_png_policy(), registry=reg)
    assert str(base.realization_identity()) == str(inside.realization_identity())


def test_linewidth_presentation_default_changes_identity() -> None:
    """A profile-authored line-width default participates in identity (P4-T10)."""
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    base = resolve_figure_realization(projection, serialization=_png_policy(), registry=reg)
    thick = resolve_figure_realization(
        projection,
        serialization=_png_policy(),
        presentation=RenderProfile(
            name="thick", version=1, width_inches=6, height_inches=6, line_width=4.0
        ),
        registry=reg,
    )
    assert str(base.realization_identity()) != str(thick.realization_identity())


# ---------------------------------------------------------------------------
# P4-T14 — transient (interactive) realization identity semantics
# ---------------------------------------------------------------------------


def test_interactive_and_serialized_realizations_differ_in_identity() -> None:
    """Interactive realization omits serialization identity (P4-T14).

    Same projection + same presentation: interactive identity is stable; the
    serialized realization adds serialization-specific identity, so the two
    differ while sharing the same projection identity.
    """
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    interactive = resolve_figure_realization(projection, serialization=None, registry=reg)
    serialized = resolve_figure_realization(projection, serialization=_png_policy(), registry=reg)
    # Same projection identity.
    assert str(interactive.realization_identity().projection_identity) == str(
        serialized.realization_identity().projection_identity
    )
    # Serialization-specific identity separates them.
    assert str(interactive.realization_identity()) != str(serialized.realization_identity())


def test_interactive_realization_identity_is_stable() -> None:
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    a = resolve_figure_realization(projection, serialization=None, registry=reg)
    b = resolve_figure_realization(projection, serialization=None, registry=reg)
    assert str(a.realization_identity()) == str(b.realization_identity())


def test_interactive_path_transfers_figure_and_preserves_projection() -> None:
    """Interactive realization hands a live figure to the caller (P4-T14/P4-T8)."""
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    identity_before = str(projection.identity())
    figure = render_figure_projection(projection, registry=reg)
    assert type(figure).__name__ == "Figure"
    assert str(projection.identity()) == identity_before
    plt.close(figure)


# ---------------------------------------------------------------------------
# P4-T16 — failure-path cleanup and rc-state restoration
# ---------------------------------------------------------------------------


def test_serialization_failure_leaks_no_figure() -> None:
    """A serialization failure must not leak a framework-owned Figure (P4-T16).

    The persistent path releases the framework-owned Figure on every exit path,
    including serialization failure.
    """
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    baseline = len(plt.get_fignums())

    # Force a serialization-path failure by removing savefig's required PNG
    # backend behavior via an invalid encoding parameter order is awkward; use
    # an unsupported-but-passing-construction parameter that savefig rejects.
    from ehp_sn.figures import realize_projection as _rp

    custom = resolve_serialization_policy(
        format="png", extra_parameters={"unknown_encoding_option": object()}
    )
    # This raises inside savefig (unknown keyword) and must not leak a figure.
    with pytest.raises(TypeError):
        _rp(projection, serialization=custom, registry=reg)
    assert len(plt.get_fignums()) == baseline


def test_renderer_failure_leaks_no_figure() -> None:
    """A scientific-renderer failure must not leak a framework-owned Figure (P4-T16).

    Register a figure whose visual realization entry raises, then confirm no
    pyplot-managed figure accumulates after the failed persistent realization.
    """
    from dataclasses import dataclass, field

    from ehp_sn.discovery import ComponentRegistry
    from ehp_sn.experiments import ComponentRef
    from ehp_sn.figures.builtin import raster_topology as rt
    from ehp_sn.figures.contracts import FIGURE_KIND, _VisualPartition

    spec = rt.RASTER_TOPOLOGY_INSPECTION_FIGURE

    def _boom(_projection):
        raise RuntimeError("renderer exploded")

    @dataclass(frozen=True, slots=True)
    class _FailingFigure:
        ref: ComponentRef = field(
            default_factory=lambda: ComponentRef.parse(rt.RASTER_TOPOLOGY_INSPECTION_REF)
        )
        kind: str = field(default=FIGURE_KIND)
        projection: object = field(default_factory=lambda: spec.projection)
        visual: _VisualPartition = field(
            default_factory=lambda: _VisualPartition(
                semantics_version=spec.visual.semantics_version,
                realize=_boom,
                protected_rc_params=spec.visual.protected_rc_params,
            )
        )
        defaults: object = field(default_factory=lambda: spec.defaults)

    registry = ComponentRegistry()
    registry.register(_FailingFigure())

    projection = _projection(registry=registry)
    baseline = len(plt.get_fignums())
    with pytest.raises(RuntimeError):
        realize_projection(projection, serialization=_png_policy(), registry=registry)
    assert len(plt.get_fignums()) == baseline


def test_failure_restores_rcparams() -> None:
    """rcParams are restored after a failed realization (P4-T16).

    The temporary ``rc_context`` must restore prior Matplotlib rc state even when
    a serialization failure occurs inside it.
    """
    import matplotlib as mpl

    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    original_dpi = mpl.rcParams["figure.figsize"]
    with pytest.raises(TypeError):
        realize_projection(
            projection,
            serialization=resolve_serialization_policy(
                format="png", extra_parameters={"unknown_encoding_option": object()}
            ),
            registry=reg,
        )
    assert mpl.rcParams["figure.figsize"] == original_dpi


# ---------------------------------------------------------------------------
# P4-T17 — rendering-environment provenance adequacy
# ---------------------------------------------------------------------------


def test_environment_provenance_records_reproducibility_fields() -> None:
    """Provenance records Matplotlib, backend, and FreeType (P4-T17)."""
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    r = realize_projection(projection, serialization=_png_policy(), registry=reg)
    env = r.environment
    assert env.matplotlib_version
    assert env.backend
    assert env.freetype_version
    assert env.to_dict()["matplotlib_version"] == env.matplotlib_version


def test_environment_provenance_separate_from_semantic_identity() -> None:
    """Environment is capable of differing while identity stays the same (P4-T17/P4-T6)."""
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    r1 = realize_projection(projection, serialization=_png_policy(), registry=reg)
    r2 = realize_projection(projection, serialization=_png_policy(), registry=reg)
    assert str(r1.realization_identity) == str(r2.realization_identity)
    # Same environment here => expect same bytes, but the model keeps identity
    # independent of the digest: identity has no backend/version field.
    assert not hasattr(r1.realization_identity, "backend")
    assert not hasattr(r1.realization_identity, "matplotlib_version")


# ---------------------------------------------------------------------------
# P4-T18 — semantic versus byte determinism contract
# ---------------------------------------------------------------------------


def test_content_digest_is_not_a_unique_byte_claim() -> None:
    """ContentDigest answers 'what bytes were produced', not uniqueness.

    Equal bytes => equal digest, and the digest is computed through the generic
    framework byte-digest operation, not a figure-owned algorithm (P4-T13/T18).
    """
    reg = effective_figure_registry()
    projection = _projection(registry=reg)
    r = realize_projection(projection, serialization=_png_policy(), registry=reg)
    assert r.content_digest.value == sha256_bytes_digest(r.bytes)
    # A different (equally valid) byte representation is not asserted equal to a
    # unique digest; the digest tracks whatever bytes were actually produced.
    assert r.content_digest.value != sha256_bytes_digest(r.bytes[:100])
