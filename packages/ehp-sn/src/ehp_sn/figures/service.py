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
from ehp_sn.digests import canonical_digest
from ehp_sn.discovery import ComponentRegistry, UnknownReferenceError
from ehp_sn.execution import LogicalRecord
from ehp_sn.experiments import ComponentRef, InvalidReferenceError
from ehp_sn.figures.contracts import (
    FIGURE_KIND,
    FigureInputCompatibilityError,
    FigureSpec,
)
from ehp_sn.figures.projection import FigureProjection, SourceRoleBinding
from ehp_sn.figures.providers import effective_figure_registry
from ehp_sn.figures.render_profile import RenderProfile
from ehp_sn.figures.scope import SCOPE_ARTIFACT, SCOPE_RECORD
from ehp_sn.planning import ReleaseCoordinate


class FigureServiceError(Exception):
    """Base class for controlled, generic figure-service failures."""


class UnknownFigureError(FigureServiceError):
    """The requested figure reference is not registered in the component catalogue.

    There is no fallback to another figure; an unknown figure is a controlled
    catalogue/component-resolution failure (Phase-1 § 19.2).
    """


class NoCompatibleFigureError(FigureServiceError):
    """``--figure auto`` resolved no compatible figure for the exact source.

    Raised when zero registered figures declare an input requirement satisfied
    by the source (a record's logical contract for record scope, or an
    artifact's record collection for artifact scope). It is a controlled
    discovery failure — not a silent fallback to another figure.
    """


class AmbiguousFigureError(FigureServiceError):
    """``--figure auto`` resolved more than one compatible figure for the source.

    Raised when two or more registered figures declare an input requirement
    satisfied by the source. There is no priority, preferred provider,
    first-match, best-match, or installation-order precedence (Phase-2 § 37).
    The caller must select an exact canonical ``FigureSpec`` reference
    explicitly.
    """


class _FigureSource(Protocol):
    """Minimal structural shape of a resolved figure source.

    The parent data-inspection operation supplies this resolved source. For
    ``record`` scope it is the committed artifact's canonical reference plus one
    exact logical record (record identity, logical contract, stable contents);
    for ``artifact`` scope it is the committed artifact's canonical reference
    plus its collection of records conforming to a declared logical contract, in
    canonical order (Phase-1 § 9 · P1-T7; Phase-4 § 19-20).

    The attributes are declared read-only because a resolved source is
    immutable by contract: the parent operation builds it, the figure path
    never mutates it (``FIG-003``), and the frozen source records
    (:class:`_ExactSource`, :class:`_CollectionSource`,
    :class:`~ehp_sn.figures.api.FigureSource`) satisfy the protocol without
    violating immutability.
    """

    @property
    def artifact_ref(self) -> str: ...

    @property
    def scope(self) -> str: ...

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
    the parent operation (Phase-1 § 10 · P1-T8). Scope is ``record``.
    """

    artifact_ref: str
    record_id: str
    schema_ref: str
    content: object
    scope: str = SCOPE_RECORD


@dataclass(frozen=True, slots=True)
class _CollectionSource:
    """An artifact-scope figure source: one committed artifact, one record collection.

    A generic collection source bound to the committed artifact plus its records
    conforming to ``schema_ref``, in the artifact's canonical record order.
    ``content`` is the ordered tuple of logical records (each carrying its exact
    record identity and stable content), so an artifact summary's ``select`` and
    ``prepare`` consume exactly the contract-conforming collection — never the
    producer identity and never a contract-specific source type (Phase-4 § 20,
    ``projection.md`` § "Source roles").

    ``record_id`` is a canonical deterministic collection identity (a digest of
    the ordered member record identifiers), so projection provenance is stable
    and independent of incidental artifact enumeration order (Phase-4 ·
    P4-ART-001).
    """

    artifact_ref: str
    schema_ref: str
    records: tuple[LogicalRecord, ...]
    content: tuple[LogicalRecord, ...]
    scope: str = SCOPE_ARTIFACT

    @property
    def record_ids(self) -> tuple[str, ...]:
        """The member record identifiers in a canonical (sorted) order.

        Canonicalizing by record identity makes the collection provenance
        independent of the incidental enumeration order of ``records``, so a
        collection under a different enumeration ordering yields the same
        projection (Phase-4 § 27 · P4-ART-001).
        """
        return tuple(sorted(record.record_id for record in self.records))

    @property
    def record_id(self) -> str:
        return canonical_digest({"artifact": self.artifact_ref, "records": list(self.record_ids)})


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

    The requirement's scope and contract must match the source's scope and
    logical contract. Incompatibility surfaces as a controlled
    figure-input-compatibility error before preparation/rendering begins —
    never as a missing key, ``AttributeError``, shape failure, or ``imshow``
    failure.
    """
    requirement = spec.projection.requirement
    if not requirement.accepts(source.schema_ref, scope=source.scope):
        raise FigureInputCompatibilityError(
            f"figure {spec.ref.canonical!r} requires source role "
            f"{requirement.role!r} at scope {requirement.scope!r} to satisfy "
            f"logical contract {requirement.contract!r}, but the resolved source "
            f"{source.record_id!r} is at scope {source.scope!r} and conforms to "
            f"{source.schema_ref!r}"
        )


def list_compatible_figures(
    registry: ComponentRegistry,
    source: _FigureSource,
) -> list[FigureSpec]:
    """List every registered ``FigureSpec`` compatible with the resolved source.

    Compatibility is figure-declared and generic (Phase-2 § 36): a figure is
    compatible when its declared ``FigureInputRequirement`` is satisfied by the
    source's scope and logical contract (``schema_ref``). A record-scope figure
    is only compatible with a record source; an artifact-scope figure is only
    compatible with an artifact source (Phase-4 · P4-SCOPE). The generic
    orchestration does **not** hard-code any producer→figure or contract→figure
    table; it iterates the ordinary figure catalogue and asks each ``FigureSpec``
    about its own declared requirement. The result order is the catalogue's
    canonical (deterministic) order (Phase-2 § 39).
    """
    result: list[FigureSpec] = []
    for definition in registry.iter(kind=FIGURE_KIND):
        spec = cast(FigureSpec, definition)
        if spec.projection.requirement.accepts(source.schema_ref, scope=source.scope):
            result.append(spec)
    return result


def resolve_auto_figure(
    registry: ComponentRegistry,
    source: _FigureSource,
) -> FigureSpec:
    """Resolve ``--figure auto`` to exactly one canonical ``FigureSpec``.

    ``auto`` is a CLI convenience token, not a scientific or projection identity
    (Phase-2 § 38). It resolves compatibility against the resolved source (scope
    and logical contract):

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
            f"no compatible figure for source {source.record_id!r} at scope "
            f"{source.scope!r} conforming to {source.schema_ref!r}"
        )
    if len(compatible) > 1:
        refs = sorted(spec.ref.canonical for spec in compatible)
        raise AmbiguousFigureError(
            f"multiple compatible figures for source {source.record_id!r} at "
            f"scope {source.scope!r} conforming to {source.schema_ref!r}: {refs}. "
            f"Select an exact canonical FigureSpec reference explicitly."
        )
    return compatible[0]


def prepare_figure(
    registry: ComponentRegistry,
    figure_ref: str,
    source: _FigureSource,
) -> FigureProjection:
    """Resolve, validate, and project one figure over one resolved source.

    ``source`` is the already-resolved source supplied by the parent operation
    (exactly one resolution; the figure layer does not select the record again —
    Phase-1 § 10 · P1-T8; Phase-4 artifact collection). This function:

    ```text
    canonical figure reference
        ↓
    ordinary catalogue resolution
        ↓
    FigureSpec
        ↓
    semantic input validation (scope + contract)
        ↓
    select()  — when the figure declares a selection resolver (Phase 3)
        ↓
    prepare()
        ↓
    FigureProjection
    ```

    Returns a ``FigureProjection`` carrying exact source provenance (for
    artifact scope, the collection identity and ordered member record
    identifiers), the exact authored + resolved selection (when declared), and
    the prepared stable view (Phase-1 § 12 · P1-T10 · Phase 3).
    """
    spec = _resolve_figure(registry, figure_ref)
    _validate_input_requirement(spec, source)
    selection = None
    if spec.projection.select is not None:
        selection = spec.projection.select(source.content)
    prepared = spec.projection.prepare(source.content)
    record_ids: tuple[str, ...] | None = None
    if source.scope == SCOPE_ARTIFACT and isinstance(source, _CollectionSource):
        record_ids = source.record_ids
    binding = SourceRoleBinding(
        role=spec.projection.requirement.role,
        artifact_ref=source.artifact_ref,
        record_id=source.record_id,
        logical_contract=source.schema_ref,
        content=prepared,
        scope=source.scope,
        record_ids=record_ids,
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


def _build_collection_source(
    committed: SubstrateArtifact,
    schema_ref: str,
) -> _CollectionSource:
    """Build the generic artifact-scope source for one committed artifact.

    The collection is the committed artifact's records conforming to
    ``schema_ref``, in the artifact's canonical record order (a deterministic,
    immutable order — never filesystem/subset/dict order). A committed artifact
    is immutable (``ART-001``), so its record collection at a release coordinate
    is stable and reproducible. This is a generic collection source bound to the
    resolved EHP-SN artifact resource; no contract-specific source type is
    introduced (Phase-4 § 20, ``projection.md`` § "Source roles").
    """
    records = tuple(record for record in committed.records if record.schema_ref == schema_ref)
    if not records:
        raise FigureServiceError(
            f"committed artifact {committed.artifact_ref!r} contains no records "
            f"conforming to logical contract {schema_ref!r} (artifact-scope figure "
            f"source is empty)"
        )
    return _CollectionSource(
        artifact_ref=committed.artifact_ref,
        schema_ref=schema_ref,
        records=records,
        content=records,
    )


def list_figures_for_artifact(
    artifact: str,
    schema_ref: str | None = None,
    *,
    artifact_root: Path | None = None,
    registry: ComponentRegistry | None = None,
) -> list[str]:
    """List figures compatible with one committed artifact's record collection.

    Resolves the committed artifact and filters its records to those conforming
    to ``schema_ref`` (the parent operation's exact artifact-scope resolution);
    when ``schema_ref`` is omitted it uses the artifact's declared output
    contract. It then lists every registered ``FigureSpec`` whose declared scope
    ``artifact`` input requirement the collection satisfies, in the catalogue's
    canonical order (Phase-4 § 19-20). It is generic: no producer→figure or
    contract→figure table is hard-coded here.
    """
    root = artifact_root if artifact_root is not None else Path("data/interim")
    committed = _resolve_artifact(artifact, root)
    schema = schema_ref if schema_ref is not None else committed.output_contract
    source = _build_collection_source(committed, schema)
    effective = registry if registry is not None else effective_figure_registry()
    compatible = list_compatible_figures(effective, source)
    return [spec.ref.canonical for spec in compatible]


def inspect_artifact_figure(
    artifact: str,
    figure_ref: str,
    *,
    artifact_root: Path | None = None,
    registry: ComponentRegistry | None = None,
) -> FigureResult:
    """Project and realize an artifact-scope figure over a committed record collection.

    This is the artifact-scope counterpart of :func:`inspect_figure`: it
    resolves the committed artifact, filters its records to those conforming to
    the requested figure's declared logical contract into a generic collection
    source, matches the requested artifact-scope figure through the ordinary
    component catalogue, validates the semantic input requirement, prepares the
    projection (including any deterministic representative selection), and
    realizes a Matplotlib Figure.

    The collection schema is taken from the requested figure's own declared
    input requirement (``requirement.contract``), so the caller stays generic
    and never names a producer or a contract-specific source type (Phase-4
    § 19-20, § 23). A figure whose requirement is not artifact-scope is a
    controlled figure-input-compatibility failure, not a silent record path.

    It performs exactly one resolution of the artifact/collection; the figure
    layer does not select the records again beyond its declared deterministic
    selection (Phase-4 § 19-20, § 23). ``artifact_root`` is the interim-data
    root used for ``artifact:`` reference resolution and defaults to the
    repository convention ``data/interim``.
    """
    root = artifact_root if artifact_root is not None else Path("data/interim")
    effective = registry if registry is not None else effective_figure_registry()
    spec = _resolve_figure(effective, figure_ref)
    requirement = spec.projection.requirement
    if requirement.scope != SCOPE_ARTIFACT:
        raise FigureInputCompatibilityError(
            f"figure {spec.ref.canonical!r} is a {requirement.scope!r}-scope "
            f"figure; an artifact-scope inspection requires a figure whose "
            f"requirement scope is {SCOPE_ARTIFACT!r} (or pass --record for a "
            f"record-scope figure)"
        )
    committed = _resolve_artifact(artifact, root)
    source = _build_collection_source(committed, requirement.contract)
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
    "inspect_artifact_figure",
    "inspect_figure",
    "list_compatible_figures",
    "list_figures_for_artifact",
    "list_figures_for_record",
    "prepare_figure",
    "render_figure_projection",
    "resolve_auto_figure",
]
