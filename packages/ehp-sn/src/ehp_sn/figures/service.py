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
from ehp_sn.figures.render_profile import RenderProfile
from ehp_sn.planning import ReleaseCoordinate


class FigureServiceError(Exception):
    """Base class for controlled, generic figure-service failures."""


class UnknownFigureError(FigureServiceError):
    """The requested figure reference is not registered in the component catalogue.

    There is no fallback to another figure; an unknown figure is a controlled
    catalogue/component-resolution failure (Phase-1 § 19.2).
    """


class NoCompatibleFigureError(FigureServiceError):
    """``--figure auto`` resolved no compatible figure for the exact source record.

    Raised when zero registered figures declare an input requirement satisfied
    by the source record's logical contract (Phase-2 § 37). It is a controlled
    discovery failure — not a silent fallback to another figure.
    """


class AmbiguousFigureError(FigureServiceError):
    """``--figure auto`` resolved more than one compatible figure for the source.

    Raised when two or more registered figures declare an input requirement
    satisfied by the source record's logical contract. There is no priority,
    preferred provider, first-match, best-match, or installation-order
    precedence (Phase-2 § 37). The caller must select an exact canonical
    ``FigureSpec`` reference explicitly.
    """


class _FigureSource(Protocol):
    """Minimal structural shape of a resolved exact source.

    The parent data-inspection operation supplies this exact resolved record:
    the committed artifact's canonical reference, the exact record identity, the
    logical contract the record conforms to, and its stable logical contents
    (Phase-1 § 9 · P1-T7).

    The attributes are declared read-only because a resolved exact source is
    immutable by contract: the parent operation builds it, the figure path never
    mutates it (``FIG-003``), and frozen source records
    (:class:`_ExactSource`, :class:`~ehp_sn.figures.api.FigureSource`) satisfy
    the protocol without violating immutability.
    """

    @property
    def artifact_ref(self) -> str: ...

    @property
    def record_id(self) -> str: ...

    @property
    def schema_ref(self) -> str: ...

    @property
    def content(self) -> object: ...


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


def list_compatible_figures(
    registry: ComponentRegistry,
    source: _FigureSource,
) -> list[FigureSpec]:
    """List every registered ``FigureSpec`` compatible with the exact source record.

    Compatibility is figure-declared and generic (Phase-2 § 36): a figure is
    compatible when its declared ``FigureInputRequirement`` is satisfied by the
    source record's logical contract (``schema_ref``). The generic orchestration
    does **not** hard-code any producer→figure or contract→figure table; it
    iterates the ordinary figure catalogue and asks each ``FigureSpec`` about its
    own declared requirement. The result order is the catalogue's canonical
    (deterministic) order (Phase-2 § 39).
    """
    result: list[FigureSpec] = []
    for definition in registry.iter(kind=FIGURE_KIND):
        spec = cast(FigureSpec, definition)
        if spec.projection.requirement.accepts(source.schema_ref):
            result.append(spec)
    return result


def resolve_auto_figure(
    registry: ComponentRegistry,
    source: _FigureSource,
) -> FigureSpec:
    """Resolve ``--figure auto`` to exactly one canonical ``FigureSpec``.

    ``auto`` is a CLI convenience token, not a scientific or projection identity
    (Phase-2 § 38). It resolves compatibility against the exact source record:

    ```text
    0 compatible    → NoCompatibleFigureError
    1 compatible    → return the exact FigureSpec
    >1 compatible   → AmbiguousFigureError
    ```

    There is no priority, preferred provider, first match, best match, or
    installation-order precedence (Phase-2 § 37). Once resolved, callers must
    use the returned ``FigureSpec``'s exact canonical reference — never retain
    ``auto`` as provenance (Phase-2 § 38).
    """
    compatible = list_compatible_figures(registry, source)
    if not compatible:
        raise NoCompatibleFigureError(
            f"no compatible figure for source record {source.record_id!r} "
            f"conforming to {source.schema_ref!r}"
        )
    if len(compatible) > 1:
        refs = sorted(spec.ref.canonical for spec in compatible)
        raise AmbiguousFigureError(
            f"multiple compatible figures for source record {source.record_id!r} "
            f"conforming to {source.schema_ref!r}: {refs}. "
            f"Select an exact canonical FigureSpec reference explicitly."
        )
    return compatible[0]


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
    select()  — when the figure declares a selection resolver (Phase 3)
        ↓
    prepare()
        ↓
    FigureProjection
    ```

    Returns a ``FigureProjection`` carrying exact source provenance, the exact
    authored + resolved selection (when declared), and the prepared stable view
    (Phase-1 § 12 · P1-T10 · Phase 3).
    """
    spec = _resolve_figure(registry, figure_ref)
    _validate_input_requirement(spec, source)
    selection = None
    if spec.projection.select is not None:
        selection = spec.projection.select(source.content)
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
        selection=selection,
    )


def render_figure_projection(
    projection: FigureProjection,
    registry: ComponentRegistry | None = None,
    *,
    presentation: RenderProfile | None = None,
) -> Any:
    """Realize a ``FigureProjection`` directly as a Matplotlib Figure.

    This is the **interactive/transient** realization path: ownership of the
    returned ``matplotlib.figure.Figure`` transfers to the caller, who controls
    its interactive lifetime (Phase-4 · P4-T8). It is the transient counterpart
    of :func:`~ehp_sn.figures.realization.realize_projection`.

    It resolves the same canonical realization request as the persistent path
    (Phase-4 · P4-T9), validates realization inputs before Matplotlib
    (P4-T15), and enforces scientific-visual precedence over presentation
    (P4-T11). The resulting effective presentation is applied within a temporary
    Matplotlib rc context, and drawing is delegated to the figure-owned visual
    implementation.

    A caller that also needs the transient realization's semantic identity (with
    serialization excluded; P4-T14) resolves via
    :func:`~ehp_sn.figures.realization.resolve_figure_realization` with
    ``serialization=None``.

    ``registry`` is optional: it re-resolves the ``FigureSpec`` from the
    catalogue when provided. When omitted, the figure is located through the
    effective framework catalogue by canonical reference.
    """
    from ehp_sn.figures.realization import resolve_figure_realization

    effective = registry if registry is not None else effective_figure_registry()
    spec = cast(FigureSpec, _resolve_figure(effective, projection.figure_ref))
    resolved = resolve_figure_realization(
        projection,
        presentation=presentation,
        serialization=None,
        registry=effective,
    )
    import matplotlib

    with matplotlib.rc_context(resolved.to_rc_params()):  # type: ignore[arg-type]
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
    resolved_figure_ref = _canonicalize_figure_ref(effective, source, figure_ref)
    projection = prepare_figure(effective, resolved_figure_ref, source)
    figure = render_figure_projection(projection, registry=effective)
    return FigureResult(projection=projection, figure=figure)


def _canonicalize_figure_ref(
    registry: ComponentRegistry,
    source: _FigureSource,
    figure_ref: str,
) -> str:
    """Canonicalize an ``auto`` convenience token to an exact FigureSpec reference.

    ``auto`` is a CLI convenience token, not a scientific or projection identity
    (Phase-2 § 38). Before projection construction it is resolved to exactly one
    canonical ``FigureSpec`` reference; from that point onward provenance
    contains only the exact resolved figure reference — never ``auto``
    (Phase-2 § 38, § 41). An explicit canonical reference is returned unchanged.
    """
    token = figure_ref.strip()
    if token == AUTO_FIGURE_TOKEN:
        resolved = resolve_auto_figure(registry, source)
        return resolved.ref.canonical
    return figure_ref


def list_figures_for_record(
    artifact: str,
    record_id: str,
    *,
    artifact_root: Path | None = None,
    registry: ComponentRegistry | None = None,
) -> list[str]:
    """List the canonical references of figures compatible with one committed record.

    Resolves exactly one committed record (the parent operation's exact-record
    resolution, P1-T8), then lists every registered ``FigureSpec`` whose declared
    input requirement the record satisfies, in the catalogue's canonical order
    (Phase-2 § 36, § 39). It is generic: no producer→figure or contract→figure
    table is hard-coded here.
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
    compatible = list_compatible_figures(effective, source)
    return [spec.ref.canonical for spec in compatible]


#: The ``auto`` convenience token for single-figure resolution (Phase-2 § 37-38).
AUTO_FIGURE_TOKEN = "auto"


__all__ = [
    "AUTO_FIGURE_TOKEN",
    "AmbiguousFigureError",
    "FigureResult",
    "FigureServiceError",
    "NoCompatibleFigureError",
    "UnknownFigureError",
    "inspect_figure",
    "list_compatible_figures",
    "list_figures_for_record",
    "prepare_figure",
    "render_figure_projection",
    "resolve_auto_figure",
]
