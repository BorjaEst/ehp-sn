"""Figure realization: the boundary between projection and serialized output.

This module implements the Phase-4 realization boundary. It takes one
already-fixed :class:`~ehp_sn.figures.projection.FigureProjection`, resolves a
single fully-resolved realization request, produces controlled serialized output
through Matplotlib's centralized path, and separates:

```text
RealizationIdentity              what visual realization was requested?
RenderingEnvironmentProvenance   what implementation environment produced it?
ContentDigest                    what exact serialized bytes were produced?
```

It does **not** rerun source resolution, scientific selection, ``prepare()``, or
scientific analysis (Phase-4 boundary; ``rendering.md`` § "Realization
boundary"). Rendering the same projection differently reuses the same scientific
view.

## Canonical resolved realization (Phase-4 · P4-T9)

There is exactly one internal semantic boundary between authored intent and
Matplotlib:

```text
authored realization request
        + FigureSpec visual defaults
        + RenderProfile
        + serialization request
        ↓  resolution (validate + enforce precedence)
ResolvedFigureRealization     ← the single effective realization state
        ↓
RealizationIdentity
        ↓
Matplotlib rendering + serialization
```

Both ``RealizationIdentity`` and the concrete rendering inputs derive from the
same :class:`ResolvedFigureRealization`. No second resolution occurs inside
rendering or serialization.

## Effective presentation identity (Phase-4 · P4-T10)

Presentation identity represents the **effective** presentation configuration
(figure defaults + profile + framework overrides), not merely a profile
name/version. :class:`ResolvedFigureRealization` carries a
:class:`~ehp_sn.figures.render_profile.ResolvedPresentation`, and
``RealizationIdentity`` digests its effective values. Ambient (unresolved)
Matplotlib state never enters this identity.

## Scientific semantics override presentation policy (Phase-4 · P4-T11)

A :class:`~ehp_sn.figures.render_profile.RenderProfile` may provide defaults
only where they do not change scientific meaning. The figure's visual partition
declares its scientifically protected rc-parameters; effective-presentation
resolution rejects any presentation input that would silently override them
(``PresentationError``) rather than reinterpreting the science.

## Figure lifecycle ownership (Phase-4 · P4-T8 / P4-T16)

```text
interactive / transient path
    caller requests a matplotlib.figure.Figure
    → ownership transfers to the caller (after successful handoff)

persistent serialization path
    framework creates the Figure solely to serialize it
    → render → serialize → release/close
```

The persistent path releases the framework-owned Figure on **every** exit path
(success, renderer failure, serialization failure) within a ``finally``, so
repeated or failed persistent rendering never accumulates framework-owned
figures.

## Centralized serialization (Phase-4 · P4-T6)

Provider code does not call ``fig.savefig(...)``. The framework serializes
through one controlled path using the fully resolved serialization policy
(format and all realization-affecting parameters explicit, never inferred from a
filename or ambient Matplotlib state).

## Semantic versus byte determinism (Phase-4 · P4-T18)

EHP-SN guarantees *semantically equivalent* output for the same resolved
realization under a compatible rendering environment; it does **not** guarantee
byte-identical PNG/SVG output across arbitrary environments.
:class:`ContentDigest` answers only *what exact serialized bytes were produced*,
not *whether they are the only byte representation of this
``RealizationIdentity``*.
"""

from __future__ import annotations

import platform
import sys
from contextlib import suppress
from dataclasses import dataclass
from typing import Any, cast

from ehp_sn.digests import canonical_digest, sha256_bytes_digest
from ehp_sn.figures.contracts import FigureSpec
from ehp_sn.figures.projection import FigureProjection, ProjectionIdentity
from ehp_sn.figures.providers import effective_figure_registry
from ehp_sn.figures.render_profile import (
    PresentationError,
    RenderProfile,
    ResolvedPresentation,
)
from ehp_sn.figures.serialization import ResolvedSerializationPolicy
from ehp_sn.figures.service import _resolve_figure


class RealizationError(Exception):
    """Base class for controlled, generic figure-realization failures.

    Raised for semantically invalid realization requests (Phase-4 · P4-T15)
    before Matplotlib drawing/serialization begins, never as a raw backend error.
    """


def _resolve_spec(projection: FigureProjection, registry: Any) -> FigureSpec:
    """Resolve the ``FigureSpec`` for a projection from the ordinary catalogue.

    Reuses the framework's single figure-resolution path
    (:func:`ehp_sn.figures.service._resolve_figure`), which resolves by kind
    through the ordinary component catalogue and maps controlled failures to
    :class:`UnknownFigureError`. There is no second figure-resolution entry.
    """
    effective = registry if registry is not None else effective_figure_registry()
    return cast(FigureSpec, _resolve_figure(effective, projection.figure_ref))


def _enforce_scientific_precedence(
    spec: FigureSpec,
    effective_rc: dict[str, object],
) -> None:
    """Reject presentation inputs that would override scientific visual semantics.

    The figure's visual partition declares its scientifically protected rc-keys.
    Any resolved effective value for a protected key that differs from the value
    the scientific visual semantics hard-codes would silently change scientific
    meaning, so the conflict fails explicitly (Phase-4 · P4-T11). Scientific
    authority always wins over presentation.
    """
    protected = spec.visual.protected_rc_params
    if not protected:
        return
    # Identify which protected keys a presentation input attempted to set. The
    # figure's own authored presentation defaults never carry scientific keys;
    # a non-empty, non-default value for a protected key signals an override
    # attempt.
    for key in protected:
        if key in effective_rc and effective_rc[key] is not None:
            raise PresentationError(
                f"presentation policy attempts to override scientifically protected "
                f"rc-parameter {key!r} owned by the figure's visual semantics; failing "
                "explicitly instead of reinterpreting scientific meaning (P4-T11)"
            )


def _resolve_effective_presentation(
    spec: FigureSpec,
    presentation: RenderProfile | None,
    *,
    scientific_overrides: dict[str, object] | None = None,
) -> ResolvedPresentation:
    """Resolve the single effective presentation configuration for a figure.

    Applies the authority order (Phase-4 · P4-T11):

    ```text
    generic/figure presentation defaults
            ↓
    RenderProfile presentation defaults
            ↓
    explicit framework/scientific overrides
    ```

    The result is a :class:`ResolvedPresentation` whose ``rc`` is the exact
    configuration the rendering path consumes; its effective values are also
    what ``RealizationIdentity`` digests (P4-T9/P4-T10).
    """
    rc: dict[str, object] = dict(spec.defaults.rc_params)
    if presentation is not None:
        rc.update(presentation.to_rc_params())
    if scientific_overrides is not None:
        rc.update(scientific_overrides)
    _enforce_scientific_precedence(spec, rc)
    return ResolvedPresentation(rc=rc, profile=presentation)


@dataclass(frozen=True, slots=True)
class ResolvedFigureRealization:
    """The single fully-resolved realization state for one projection (P4-T9).

    Produced by :func:`resolve_figure_realization` from the authored realization
    request. It is the **only** state from which both ``RealizationIdentity`` and
    the concrete rendering/serialization inputs are derived; no second
    resolution occurs inside rendering or serialization.

    ``projection`` is the already-fixed ``FigureProjection`` (never re-resolved
    or re-prepared). ``presentation`` is the effective resolved presentation.
    ``serialization`` is the validated resolved serialization policy.
    ``visual_semantics_ref`` / ``visual_semantics_version`` identify the
    figure's scientific visual-encoding semantics.
    """

    projection: FigureProjection
    presentation: ResolvedPresentation
    serialization: ResolvedSerializationPolicy | None
    visual_semantics_ref: str
    visual_semantics_version: int

    def to_rc_params(self) -> dict[str, object]:
        """The exact effective rc-parameter configuration rendering consumes."""
        return self.presentation.rc

    def realization_identity(self) -> RealizationIdentity:
        """Compute the realization identity from the same resolved state rendered.

        ``serialization_identity`` is ``None`` for a transient interactive
        realization, which omits serialization-specific identity inputs
        (Phase-4 · P4-T14); a serialized realization includes them.
        """
        return RealizationIdentity(
            projection_identity=self.projection.identity(),
            visual_semantics_ref=self.visual_semantics_ref,
            visual_semantics_version=self.visual_semantics_version,
            presentation_identity=self.presentation.identity(),
            serialization_identity=(
                self.serialization.identity() if self.serialization is not None else None
            ),
        )


def resolve_figure_realization(
    projection: FigureProjection,
    *,
    presentation: RenderProfile | None = None,
    serialization: ResolvedSerializationPolicy | None = None,
    registry: Any = None,
    scientific_overrides: dict[str, object] | None = None,
) -> ResolvedFigureRealization:
    """Resolve one canonical, fully-effective realization request (P4-T9/T10/T15).

    Validates the realization inputs (serialization format/DPI/parameters and
    presentation/scientific precedence) **before** Matplotlib is invoked,
    raising controlled :class:`SerializationError` / :class:`PresentationError`
    / :class:`RealizationError` on an invalid request. Returns the single
    resolved state from which identity and rendering both derive.

    ``serialization=None`` denotes a transient interactive realization (no
    serialization-specific identity inputs).
    """
    spec = _resolve_spec(projection, registry)
    effective_presentation = _resolve_effective_presentation(
        spec, presentation, scientific_overrides=scientific_overrides
    )
    if serialization is not None:
        serialization.validate()  # controlled failure before drawing (P4-T15)
    return ResolvedFigureRealization(
        projection=projection,
        presentation=effective_presentation,
        serialization=serialization,
        visual_semantics_ref=projection.figure_ref,
        visual_semantics_version=spec.visual.semantics_version,
    )


@dataclass(frozen=True, slots=True)
class RenderingEnvironmentProvenance:
    """The concrete implementation environment that produced a realization.

    Captured as separate provenance, never merged into semantic
    :class:`RealizationIdentity` (Phase-4 · P4-T5/P4-T17). Two executions may
    share the same projection and realization identity yet differ in
    rendering-environment provenance or content digest when backend/library/font
    behavior differs.

    The Phase-4 reproducibility policy always records ``matplotlib_version`` and
    ``backend`` (renderer). ``freetype_version`` is captured because text
    rasterization is relevant to persistent publication output. Python/platform
    values are informational and recorded for completeness; none is semantic
    identity.
    """

    matplotlib_version: str
    backend: str
    freetype_version: str
    python_version: str
    platform: str

    def to_dict(self) -> dict[str, str]:
        return {
            "matplotlib_version": self.matplotlib_version,
            "backend": self.backend,
            "freetype_version": self.freetype_version,
            "python_version": self.python_version,
            "platform": self.platform,
        }


def record_rendering_environment() -> RenderingEnvironmentProvenance:
    """Capture the current rendering environment (Phase-4 · P4-T17).

    Records Matplotlib version, the active backend/renderer, and FreeType version
    (relevant where text rasterization affects persistent output), plus
    informational Python/platform values.
    """
    import matplotlib
    from matplotlib import ft2font

    return RenderingEnvironmentProvenance(
        matplotlib_version=matplotlib.__version__,
        backend=matplotlib.get_backend(),
        freetype_version=getattr(ft2font, "__freetype_version__", "unknown"),
        python_version=sys.version.split()[0],
        platform=platform.platform(),
    )


@dataclass(frozen=True, slots=True)
class ContentDigest:
    """The exact identity of serialized content produced by one realization.

    ``value`` is the ``sha256:<hex>`` digest of the exact serialized bytes,
    computed through the generic framework byte-digest mechanism
    (:func:`ehp_sn.digests.sha256_bytes_digest`) — not a figure-owned hashing
    algorithm (Phase-4 · P4-T13).

    Conceptually separate from semantic :class:`RealizationIdentity`
    (``rendering.md`` § "Semantic and byte reproducibility"). It answers *what
    exact serialized bytes were produced*, not *whether they are the only byte
    representation of this realization identity* (Phase-4 · P4-T18).
    """

    value: str

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class RealizationIdentity:
    """The intended visual realization of one exact scientific projection.

    Semantically:

    ```text
    RealizationIdentity =
        ProjectionIdentity
        + visual-semantics identity/version
        + effective-presentation identity
        (+ serialization-policy identity, when serialized)
    ```

    ``presentation_identity`` is the digest of the **effective** presentation
    state, so any intentional presentation input that alters the effective
    configuration changes realization identity (Phase-4 · P4-T10).
    ``serialization_identity`` is ``None`` for a transient interactive
    realization (Phase-4 · P4-T14); a serialized realization carries it.

    Projection-only changes change ``ProjectionIdentity`` and therefore
    ``RealizationIdentity``. Visual/presentation/serialization changes preserve
    ``ProjectionIdentity`` and change ``RealizationIdentity`` (``rendering.md``
    § ``RealizationIdentity``). Destination/placement is never part of this
    identity.
    """

    projection_identity: ProjectionIdentity
    visual_semantics_ref: str
    visual_semantics_version: int
    presentation_identity: str
    serialization_identity: str | None

    def payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "projection_identity": str(self.projection_identity),
            "visual_semantics_ref": self.visual_semantics_ref,
            "visual_semantics_version": self.visual_semantics_version,
            "presentation_identity": self.presentation_identity,
        }
        if self.serialization_identity is not None:
            payload["serialization_identity"] = self.serialization_identity
        return payload

    def __str__(self) -> str:
        return canonical_digest(self.payload())


@dataclass(frozen=True, slots=True)
class RealizedFigure:
    """One serialized realization produced by a single controlled framework path.

    Carries the exact serialized bytes, their :class:`ContentDigest`, the
    semantic :class:`RealizationIdentity`, and the distinct
    :class:`RenderingEnvironmentProvenance`. The transient Matplotlib Figure
    that produced these bytes is **not** retained: on the persistent path the
    framework owns it and closes it after serialization (P4-T8/P4-T16).

    ``destination`` is deliberately **not** part of :class:`RealizationIdentity`;
    changing only the destination/placement does not change the semantic
    realization. A parent operation owns destination and persistence
    (``integration.md`` § "Destination and sinks").
    """

    format: str
    bytes: bytes
    content_digest: ContentDigest
    realization_identity: RealizationIdentity
    environment: RenderingEnvironmentProvenance


def _draw_figure(
    projection: FigureProjection,
    spec: FigureSpec,
    resolved: ResolvedFigureRealization,
) -> Any:
    """Draw the projection as a Matplotlib Figure within a controlled rc context.

    Delegates drawing to the figure-owned scientific visual implementation
    (``spec.visual.realize``) under the rc configuration resolved into
    :class:`ResolvedFigureRealization`. The returned Figure is transient;
    ownership is decided by the caller (interactive path transfers it; persistent
    path serializes and closes it).
    """
    import matplotlib

    # matplotlib.rc_context is typed over a closed set of rc-parameter Literals;
    # the effective presentation configuration is a generic name→value mapping
    # resolved by this framework, so the narrowed rc_context signature does not
    # apply. The controlled configuration is applied only within this context.
    with matplotlib.rc_context(resolved.to_rc_params()):  # type: ignore[arg-type]
        return spec.visual.realize(projection)


def _serialize_bytes(
    figure: Any,
    *,
    serialization: ResolvedSerializationPolicy,
) -> bytes:
    """Serialize a Matplotlib Figure through a single controlled framework path.

    Uses the fully resolved serialization policy: the format is explicit, and
    all realization-affecting encoding parameters are drawn from the resolved
    policy — never inferred from a filename, ambient ``rcParams``, or
    Matplotlib defaults. The figure is not closed here; the persistent path
    closes it after serialization.
    """
    import io

    buffer = io.BytesIO()
    params: dict[str, object] = {}
    if serialization.format == "png":
        params["dpi"] = serialization.dpi
    params.update(serialization.extra_parameters)
    figure.savefig(buffer, format=serialization.format, **params)  # type: ignore[arg-type]
    return buffer.getvalue()


def _close_figure(figure: Any) -> None:
    """Release a framework-owned transient Matplotlib Figure (P4-T8/P4-T16).

    Closes the figure so persistent rendering (including failed attempts) does
    not accumulate framework-owned figures.
    """
    import matplotlib.pyplot as plt

    with suppress(Exception):  # pragma: no cover - clear() is best-effort
        figure.clear()
    plt.close(figure)


def realize_projection(
    projection: FigureProjection,
    *,
    serialization: ResolvedSerializationPolicy,
    presentation: RenderProfile | None = None,
    registry: Any = None,
    scientific_overrides: dict[str, object] | None = None,
) -> RealizedFigure:
    """Serialize one already-fixed projection through the controlled framework path.

    This is the persistent realization entry point (Phase-4 · P4-T1, P4-T6,
    P4-T8). It resolves one canonical realization request (P4-T9), validates it
    before Matplotlib (P4-T15), draws, serializes, and releases the
    framework-owned Figure on every exit path (P4-T16). It never reruns
    selection or preparation.

    ```text
    FigureProjection
        ↓  resolve_figure_realization (validate + effective presentation)
    ResolvedFigureRealization
        ↓
    RealizationIdentity  ← from the same resolved state rendered
        ↓
    controlled Matplotlib realization
        ↓
    serialized bytes
        ↓
    RealizedFigure (identity + content digest + environment provenance)
    ```
    """

    resolved = resolve_figure_realization(
        projection,
        presentation=presentation,
        serialization=serialization,
        registry=registry,
        scientific_overrides=scientific_overrides,
    )
    spec = _resolve_spec(projection, registry)

    figure = None
    try:
        figure = _draw_figure(projection, spec, resolved)
        raw = _serialize_bytes(figure, serialization=serialization)
    finally:
        # Release the framework-owned Figure on every exit path — success,
        # renderer failure, or serialization failure (P4-T16). The rc state is
        # restored by rc_context exiting.
        if figure is not None:
            _close_figure(figure)

    return RealizedFigure(
        format=serialization.format,
        bytes=raw,
        content_digest=ContentDigest(sha256_bytes_digest(raw)),
        realization_identity=resolved.realization_identity(),
        environment=record_rendering_environment(),
    )


__all__ = [
    "ContentDigest",
    "RealizationError",
    "RealizationIdentity",
    "RealizedFigure",
    "RenderingEnvironmentProvenance",
    "ResolvedFigureRealization",
    "resolve_figure_realization",
    "realize_projection",
    "record_rendering_environment",
]
