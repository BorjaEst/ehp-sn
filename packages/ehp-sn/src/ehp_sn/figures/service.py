"""Generic figure orchestration service (Phase 1 bootstrap slice).

This module owns the generic figure orchestration: resolving a requested figure
through the ordinary component catalogue, validating its semantic input
requirement against the exact resolved source, preparing the projection, and
realizing it directly as a Matplotlib Figure.

It is deliberately generic. It contains no raster/producer-specific semantic
branching (Phase-1 § 18): contract-specific behavior belongs to the ``FigureSpec``
contributed through the catalogue, not here.

The realization path is:

```text
FigureProjection
        ↓
figure-owned visual implementation
        ↓
matplotlib.figure.Figure
        ↓
Axes / Artists
```

There is no intermediate EHP-owned graphics representation (Phase-1 § 14 ·
P1-T12).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

from ehp_sn.artifacts import (
    StoreError,
    SubstrateArtifact,
    load_release,
    resolve_release,
)
from ehp_sn.artifacts.manifest import ManifestParseError
from ehp_sn.discovery import ComponentRegistry, UnknownReferenceError
from ehp_sn.experiments import ComponentRef, InvalidReferenceError
from ehp_sn.figures.contracts import (
    FIGURE_KIND,
    FigureInputCompatibilityError,
    FigureSpec,
)
from ehp_sn.figures.projection import FigureProjection, SourceRoleBinding
from ehp_sn.figures.providers import effective_figure_registry
from ehp_sn.planning import ReleaseCoordinate


class FigureServiceError(Exception):
    """Base class for controlled, generic figure-service failures."""


class UnknownFigureError(FigureServiceError):
    """The requested figure reference is not registered in the component catalogue.

    There is no fallback to another figure; an unknown figure is a controlled
    catalogue/component-resolution failure (Phase-1 § 19.2).
    """


class _FigureSource(Protocol):
    """Minimal structural shape of a resolved exact source.

    The parent data-inspection operation supplies this exact resolved record:
    the committed artifact's canonical reference, the exact record identity, the
    logical contract the record conforms to, and its stable logical contents
    (Phase-1 § 9 · P1-T7).
    """

    artifact_ref: str
    record_id: str
    schema_ref: str
    content: object


@dataclass(frozen=True, slots=True)
class _ExactSource:
    """The exact resolved source: committed artifact identity plus one logical record.

    Combines the committed artifact's canonical reference with an exact logical
    record (record identity, logical contract, stable contents) into the single
    source the figure consumes. This is the one exact resolution performed by
    the parent operation (Phase-1 § 10 · P1-T8).
    """

    artifact_ref: str
    record_id: str
    schema_ref: str
    content: object


def _resolve_artifact(artifact: str, root: Path) -> SubstrateArtifact:
    """Resolve a committed artifact by path or canonical ``artifact:`` reference.

    Reuses the existing durable artifact-resolution machinery
    (``load_release`` / ``resolve_release``); it is generic artifact resolution,
    not figure-specific, and builds no parallel artifact resolver (ARCH-014).
    """
    reference = artifact.strip()
    if reference.lower().startswith("artifact:"):
        try:
            parsed = ComponentRef.parse(reference)
        except InvalidReferenceError as exc:
            raise FigureServiceError(f"malformed artifact reference: {artifact}") from exc
        if parsed.kind != "artifact":
            raise FigureServiceError(f"reference {artifact} does not denote an artifact")
        family, _, variant = parsed.name.partition("/")
        if not variant:
            raise FigureServiceError(f"artifact reference {artifact} must name <family>/<variant>")
        coordinate = ReleaseCoordinate(family=family, variant=variant, release=parsed.version)
        try:
            return resolve_release(root, coordinate)
        except (StoreError, ManifestParseError) as exc:
            raise FigureServiceError(str(exc)) from exc
    try:
        return load_release(Path(reference))
    except (StoreError, ManifestParseError) as exc:
        raise FigureServiceError(str(exc)) from exc


def _resolve_figure(registry: ComponentRegistry, figure_ref: str) -> FigureSpec:
    """Resolve a ``FigureSpec`` through the ordinary component catalogue.

    The figure must resolve by kind. An invalid/unknown reference produces the
    normal controlled component-resolution failure, mapped to
    :class:`UnknownFigureError` (Phase-1 § 19.2).
    """
    try:
        parsed = ComponentRef.parse(figure_ref)
    except InvalidReferenceError as exc:
        raise UnknownFigureError(f"invalid figure reference: {figure_ref!r}") from exc
    if parsed.kind != FIGURE_KIND:
        raise UnknownFigureError(f"reference {figure_ref} does not denote a figure")
    try:
        definition = registry.resolve(parsed)
    except UnknownReferenceError as exc:
        raise UnknownFigureError(
            f"unknown figure: {figure_ref!r} is not registered in the component catalogue"
        ) from exc
    spec = cast(FigureSpec, definition)
    if spec.kind != FIGURE_KIND:
        raise UnknownFigureError(f"registered definition {spec.ref.canonical!r} is not a figure")
    return spec


def _validate_input_requirement(spec: FigureSpec, source: _FigureSource) -> None:
    """Validate the figure's declared semantic input requirement (P1-T6).

    The requirement's contract must equal the source record's logical contract.
    Incompatibility surfaces as a controlled figure-input-compatibility error
    before preparation/rendering begins — never as a missing key,
    ``AttributeError``, shape failure, or ``imshow`` failure.
    """
    requirement = spec.projection.requirement
    if not requirement.accepts(source.schema_ref):
        raise FigureInputCompatibilityError(
            f"figure {spec.ref.canonical!r} requires source role "
            f"{requirement.role!r} to satisfy logical contract "
            f"{requirement.contract!r}, but the exact resolved record "
            f"{source.record_id!r} conforms to {source.schema_ref!r}"
        )


def prepare_figure(
    registry: ComponentRegistry,
    figure_ref: str,
    source: _FigureSource,
) -> FigureProjection:
    """Resolve, validate, and project one figure over one exact resolved source.

    ``source`` is the already-resolved exact record supplied by the parent
    ``data inspect`` operation (exactly one resolution; the figure layer does
    not select the record again — Phase-1 § 10 · P1-T8). This function:

    ```text
    canonical figure reference
        ↓
    ordinary catalogue resolution
        ↓
    FigureSpec
        ↓
    semantic input validation
        ↓
    prepare()
        ↓
    FigureProjection
    ```

    Returns a ``FigureProjection`` carrying exact source provenance and the
    prepared stable view (Phase-1 § 12 · P1-T10).
    """
    spec = _resolve_figure(registry, figure_ref)
    _validate_input_requirement(spec, source)
    prepared = spec.projection.prepare(source.content)
    binding = SourceRoleBinding(
        role=spec.projection.requirement.role,
        artifact_ref=source.artifact_ref,
        record_id=source.record_id,
        logical_contract=source.schema_ref,
        content=prepared,
    )
    return FigureProjection(
        figure_ref=spec.ref.canonical,
        projection_semantics_version=spec.projection.semantics_version,
        preparation_version=spec.projection.preparation_version,
        source=binding,
        content=prepared,
    )


def render_figure_projection(
    projection: FigureProjection,
    registry: ComponentRegistry | None = None,
) -> Any:
    """Realize a ``FigureProjection`` directly as a Matplotlib Figure.

    Resolves the figure (already resolved in :func:`prepare_figure`) to obtain
    its visual partition, applies the figure's private/provisional presentation
    defaults within a temporary Matplotlib rc context, and delegates drawing to
    the figure-owned visual implementation. Returns the transient
    ``matplotlib.figure.Figure``.

    ``registry`` is optional: it re-resolves the ``FigureSpec`` from the
    catalogue when provided. When omitted, the figure is located through the
    effective framework catalogue by canonical reference.
    """
    effective = registry if registry is not None else effective_figure_registry()
    spec = cast(FigureSpec, _resolve_figure(effective, projection.figure_ref))

    import matplotlib

    with matplotlib.rc_context(dict(spec.defaults.rc_params)):
        return spec.visual.realize(projection)


@dataclass(frozen=True, slots=True)
class FigureResult:
    """The outcome of a phase-1 ``data inspect --figure`` request.

    Bundles the ``FigureProjection`` (exact provenance + prepared view) and the
    transient ``matplotlib.figure.Figure`` for interactive display. The figure
    service itself does not require a graphical desktop; interactive display is
    a separate CLI/runtime concern (Phase-1 § 16 · P1-T14).
    """

    projection: FigureProjection
    figure: Any


def inspect_figure(
    artifact: str,
    record_id: str,
    figure_ref: str,
    *,
    artifact_root: Path | None = None,
    registry: ComponentRegistry | None = None,
) -> FigureResult:
    """Resolve one committed record, project the requested figure, and realize it.

    This is the phase-1 entry point for ``data inspect ARTIFACT --record RECORD_ID
    --figure FIGURE_REF``. It resolves exactly one committed record (the parent
    operation's exact-record resolution, P1-T8), matches it to the requested
    figure through the ordinary component catalogue, validates the semantic input
    requirement, prepares the projection, and realizes a Matplotlib Figure.

    It performs exactly one resolution of the inspected record; the figure layer
    does not select the record again. ``artifact_root`` is the interim-data root
    used for ``artifact:`` reference resolution and defaults to the repository
    convention ``data/interim``.
    """
    root = artifact_root if artifact_root is not None else Path("data/interim")
    committed = _resolve_artifact(artifact, root)
    record = committed.record(record_id)
    if record is None:
        raise FigureServiceError(
            f"record {record_id!r} not found in committed artifact {committed.artifact_ref}"
        )
    source = _ExactSource(
        artifact_ref=committed.artifact_ref,
        record_id=record.record_id,
        schema_ref=record.schema_ref,
        content=record.content,
    )
    effective = registry if registry is not None else effective_figure_registry()
    projection = prepare_figure(effective, figure_ref, source)
    figure = render_figure_projection(projection, registry=effective)
    return FigureResult(projection=projection, figure=figure)


__all__ = [
    "FigureResult",
    "FigureServiceError",
    "UnknownFigureError",
    "inspect_figure",
    "prepare_figure",
    "render_figure_projection",
]
