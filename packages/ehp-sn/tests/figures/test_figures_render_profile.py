"""Presentation-policy tests for :mod:`ehp_sn.figures.render_profile`.

These validate the Phase-4 presentation-policy contract
(``docs/docs/framework/figures/rendering.md`` § "RenderProfile"; Phase-4 ·
P4-T2/P4-T10/P4-T11):

* a ``RenderProfile`` owns presentation only and never changes projection;
* effective-presentation identity closes over figure defaults + profile values
  (P4-T10), so any intentional presentation input that alters the effective
  configuration changes realization identity;
* scientific visual semantics override presentation policy (P4-T11): a protected
  scientific rc-parameter cannot be silently replaced by a profile and instead
  fails explicitly via :class:`PresentationError`.

Headless Matplotlib is not required to construct profiles; the scientific-precedence
test calls the frame resolution path and so uses the Agg backend.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless backend for the precedence test

import pytest
from ehp_sn.figures import (
    PresentationError,
    RenderProfile,
    effective_figure_registry,
    prepare_figure,
    resolve_figure_realization,
    resolve_serialization_policy,
)
from ehp_sn.figures.service import _ExactSource

_FIGURE_REF = "figure:raster-topology-inspection/v1"


def _projection(registry=None):
    reg = registry if registry is not None else effective_figure_registry()
    return prepare_figure(
        reg,
        _FIGURE_REF,
        _ExactSource(
            artifact_ref="artifact:dg/v1",
            record_id="sha256:AAA",
            schema_ref="raster-topology/v1",
            content={
                "domain": {"height": 3, "width": 4, "position_count": 12},
                "passable": [True] * 12,
            },
        ),
    )


def _png():
    return resolve_serialization_policy(format="png")


# ---------------------------------------------------------------------------
# P4-T2 / P4-T10 — presentation owns presentation; identity is effective
# ---------------------------------------------------------------------------


def test_profile_owns_presentation_only() -> None:
    """A RenderProfile has no scientific-view selection fields (P4-T2)."""
    profile = RenderProfile(name="inspection", version=1, width_inches=6, height_inches=6)
    for field in ("cell_id", "episode_id", "selection_policy", "metric", "checkpoint", "split"):
        assert not hasattr(profile, field)
    rc = profile.to_rc_params()
    assert "figure.figsize" in rc
    assert "font.size" in rc


def test_profile_identity_differs_by_value_not_name() -> None:
    """Two profiles differing only in an effective value differ in identity (P4-T10)."""
    a = RenderProfile(name="x", version=1, width_inches=6, height_inches=6, font_size=10)
    b = RenderProfile(name="x", version=1, width_inches=6, height_inches=6, font_size=22)
    assert a.identity() != b.identity()


def test_profile_to_rc_params_is_presentation() -> None:
    profile = RenderProfile(name="pub", version=1, width_inches=12, height_inches=8, marker_size=3.0)
    rc = profile.to_rc_params()
    assert rc["figure.figsize"] == (12.0, 8.0)
    assert rc["lines.markersize"] == 3.0


# ---------------------------------------------------------------------------
# P4-T11 — scientific visual semantics override presentation policy
# ---------------------------------------------------------------------------


def test_profile_typography_and_size_overrides_accepted() -> None:
    """Presentation-only overrides (typography, physical size) are accepted (P4-T11)."""
    reg = effective_figure_registry()
    projection = _projection(reg)
    resolved = resolve_figure_realization(
        projection,
        serialization=_png(),
        presentation=RenderProfile(
            name="pub", version=1, width_inches=12, height_inches=8, font_size=16
        ),
        registry=reg,
    )
    assert resolved.to_rc_params()["figure.figsize"] == (12.0, 8.0)
    assert resolved.to_rc_params()["font.size"] == 16


def test_profile_scientific_normalization_override_rejected() -> None:
    """A profile attempting to override a scientific mapping fails explicitly (P4-T11).

    The raster figure's passability colour mapping is scientific visual
    semantics; a profile trying to set it is rejected with a controlled
    :class:`PresentationError` rather than silently reinterpreted.
    """
    reg = effective_figure_registry()
    projection = _projection(reg)
    with pytest.raises(PresentationError):
        resolve_figure_realization(
            projection,
            serialization=_png(),
            presentation=RenderProfile(
                name="bad",
                version=1,
                width_inches=6,
                height_inches=6,
                extra_rc_params={"image.cmap": "gray"},
            ),
            registry=reg,
        )
