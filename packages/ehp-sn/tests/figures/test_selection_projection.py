"""Framework selection provenance in projection identity (Phase 3).

These tests exercise the generic selection extension to the
:mod:`ehp_sn.figures.projection` boundary that Phase 3 introduces (anticipated
by Phase-1 § 12 · P1-T10): a ``FigureProjection`` may carry authored + resolved
selection provenance, and that provenance participates in ``ProjectionIdentity``
while presentation never does.

They build generic ``ResolvedFigureSelection`` values directly (no research
dependencies) to prove the framework contract is generic and reusable by any
figure, including the Phase-3 research figure.
"""

from __future__ import annotations

from ehp_sn.figures import FigureProjection, ResolvedFigureSelection
from ehp_sn.figures.projection import SourceRoleBinding

_FIGURE_REF = "figure:example/v1"


def _projection(
    *,
    selection: ResolvedFigureSelection | None,
    record_id: str = "sha256:AAA",
) -> FigureProjection:
    return FigureProjection(
        figure_ref=_FIGURE_REF,
        projection_semantics_version=1,
        preparation_version=1,
        source=SourceRoleBinding(
            role="analysis",
            artifact_ref="artifact:hpc/v1",
            record_id=record_id,
            logical_contract="hpc-analysis/v1",
            content={"stable": True},
        ),
        content={"prepared": True},
        selection=selection,
    )


def _selection(
    ref: str = "top-k",
    version: int = 1,
    params: object = {"count": 8},
    resolved: tuple[object, ...] = ("a", "b"),
) -> ResolvedFigureSelection:
    return ResolvedFigureSelection(
        selection_ref=ref,
        selection_version=version,
        parameters=params,
        resolved_identities=resolved,
    )


def test_projection_without_selection_has_none() -> None:
    projection = _projection(selection=None)
    assert projection.selection is None


def test_selection_changes_projection_identity() -> None:
    no_selection = _projection(selection=None)
    with_selection = _projection(selection=_selection())
    assert str(no_selection.identity()) != str(with_selection.identity())


def test_same_selection_same_identity() -> None:
    a = _projection(selection=_selection())
    b = _projection(selection=_selection())
    assert str(a.identity()) == str(b.identity())


def test_selection_parameters_change_identity() -> None:
    a = _projection(selection=_selection(params={"count": 8}))
    b = _projection(selection=_selection(params={"count": 12}))
    assert str(a.identity()) != str(b.identity())


def test_selection_semantics_version_changes_identity() -> None:
    a = _projection(selection=_selection(version=1))
    b = _projection(selection=_selection(version=2))
    assert str(a.identity()) != str(b.identity())


def test_different_selection_policy_same_entities_different_identity() -> None:
    """Different authored selection policies that resolve to the same entities
    remain different projection provenance (P3-T5)."""
    a = _projection(selection=_selection(ref="top-k", resolved=("x", "y")))
    b = _projection(selection=_selection(ref="first-n", resolved=("x", "y")))
    assert str(a.identity()) != str(b.identity())


def test_resolved_identities_change_identity() -> None:
    a = _projection(selection=_selection(resolved=("x", "y")))
    b = _projection(selection=_selection(resolved=("x", "z")))
    assert str(a.identity()) != str(b.identity())


def test_different_source_changes_identity_with_selection() -> None:
    a = _projection(selection=_selection(), record_id="sha256:AAA")
    b = _projection(selection=_selection(), record_id="sha256:BBB")
    assert str(a.identity()) != str(b.identity())


def test_presentation_does_not_participate_in_identity() -> None:
    """Projection identity must not depend on layout/presentation fields.

    The projection carries no width/height/font/dpi/backend/format fields even
    when it has a selection (P3-T22).
    """
    projection = _projection(selection=_selection())
    for field in (
        "width",
        "height",
        "font",
        "dpi",
        "backend",
        "serialization_format",
        "panel_layout",
        "figure_figsize",
        "font_size",
    ):
        assert not hasattr(projection, field)
