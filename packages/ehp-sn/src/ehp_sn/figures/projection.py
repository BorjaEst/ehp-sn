"""Figure projection and projection identity (Phase 1 bootstrap slice).

This module implements the projection boundary defined by
``docs/docs/framework/figures/projection.md`` for the Phase-1 walking skeleton:
a ``FigureProjection`` is the provenance-bearing boundary representing one exact
stable scientific/structural view before presentation realization.

For this slice the projection carries:

```text
figure projection semantics/version
semantic source role
exact artifact/resource identity
exact record identity
logical contract
authored + resolved selection (Phase 3)
preparation semantics/version
prepared stable view
```

Phase 1 deliberately shipped no figure-specific selection field (P1-T10); the
Phase-1 specification records that real authored versus resolved scientific
selection is first exercised by the HPC validation slice. Phase 3 therefore adds
generic selection provenance to the projection: ``ResolvedFigureSelection``
carries the authored selection semantics (identity/version + parameters) and the
exact resolved identities. A figure without a selection resolver declares
``selection=None`` and its projection identity is unchanged.

``ProjectionIdentity`` is computed only from semantic/provenance inputs. It never
reads visual, defaults, Matplotlib, typography, dimensions, backend, or
serialization fields (Phase-1 § 12 · P1-T10; ``projection.md`` § "Projection
identity"). It is not a figure-specific content digest; existing EHP-SN identity
and canonical-digest mechanisms are reused for provenance values.
"""

from __future__ import annotations

from dataclasses import dataclass

from ehp_sn.digests import canonical_digest
from ehp_sn.figures.scope import SCOPE_ARTIFACT, SCOPE_RECORD


@dataclass(frozen=True, slots=True)
class SourceRoleBinding:
    """The exact authoritative source bound to one figure role.

    ``role`` is the semantic role this source satisfies for the figure (for
    example ``topology``). ``scope`` is the source granularity: ``record``
    (exactly one committed logical record) or ``artifact`` (a committed
    artifact's collection of records conforming to the declared logical
    contract). Phase-4 artifact summaries use ``scope="artifact"`` over a
    generic collection source — never a producer identity (Phase-4 § 19-20).

    For ``record`` scope the source identity fields are the exact committed
    artifact/resource and record identity that the parent operation resolved
    (Phase-1 § 9 · P1-T7): an exact record of a committed artifact, its logical
    contract, and its stable logical contents.

    For ``artifact`` scope ``record_id`` holds a canonical deterministic
    collection identity (a digest of the ordered member record identifiers)
    and ``record_ids`` carries the exact ordered member record identifiers, so
    projection provenance identifies the whole collection without depending on
    artifact enumeration order (Phase-4 · P4-ART-001).
    """

    role: str
    artifact_ref: str
    record_id: str
    logical_contract: str
    content: object
    scope: str = SCOPE_RECORD
    record_ids: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class ResolvedFigureSelection:
    """Authored and resolved selection provenance for one projection (Phase 3).

    ``selection_ref`` and ``selection_version`` identify the authored selection
    semantics (for example ``top-spatial-information-cells`` at version 1);
    ``parameters`` is the authored parameter set (for example ``{"count": 8}``);
    ``resolved_identities`` is the exact, deterministically ordered set of
    entities resolved against the exact authoritative source.

    Both the authored semantics and the exact resolved identities are
    projection provenance: two different authored policies that resolve to the
    same identities remain different provenance (``projection.md`` §
    ``ResolvedFigureSelection``). ``parameters`` must be JSON-canonicalizable
    so it can participate in identity (``projection.md`` § "Projection identity").
    """

    selection_ref: str
    selection_version: int
    parameters: object
    resolved_identities: tuple[object, ...]

    def identity_input(self) -> object:
        """The canonical identity-relevant value of this selection."""
        return {
            "selection_ref": self.selection_ref,
            "selection_version": self.selection_version,
            "parameters": self.parameters,
            "resolved_identities": list(self.resolved_identities),
        }


@dataclass(frozen=True, slots=True)
class FigureProjection:
    """The provenance-bearing boundary for one exact prepared scientific view.

    Represents the exact stable view prepared for this figure before
    presentation realization. It never carries figure width/height, font, DPI,
    backend, serialization format, output path, or interactive GUI state
    (Phase-1 § 12 · P1-T10).

    ``content`` is the prepared stable scientific/structural view (opaque to the
    generic framework). Once incorporated into the projection it is immutable by
    contract; renderers must not mutate it.

    ``selection`` carries authored + resolved selection provenance when the
    figure declares a selection resolver; it is ``None`` for figures without
    scientific selection (Phase 3).
    """

    figure_ref: str
    projection_semantics_version: int
    preparation_version: int
    source: SourceRoleBinding
    content: object
    selection: ResolvedFigureSelection | None = None

    def identity(self) -> ProjectionIdentity:
        """Compute the projection identity from semantic/provenance inputs only."""
        return ProjectionIdentity(
            figure_ref=self.figure_ref,
            projection_semantics_version=self.projection_semantics_version,
            preparation_version=self.preparation_version,
            artifact_ref=self.source.artifact_ref,
            record_id=self.source.record_id,
            record_ids=self.source.record_ids,
            scope=self.source.scope,
            logical_contract=self.source.logical_contract,
            selection=self.selection,
        )


@dataclass(frozen=True, slots=True)
class ProjectionIdentity:
    """A figure's exact semantic/provenance identity (Phase 1 + Phase 3 selection).

    Determined by projection-semantic inputs:

    ```text
    figure projection semantics (reference + version)
    preparation semantics/version
    exact authoritative source identities (scope, artifact, record/collection,
        logical contract)
    authored selection semantics/version + parameters (when selection applies)
    exact resolved selected identities (when selection applies)
    ```

    For ``artifact`` scope the collection's ordered member record identifiers
    participate in identity, so a different committed collection is a different
    projection (Phase-4 · P4-ART-001). Presentation-only changes (panel
    placement, physical size, typography, DPI, serialization format, style) do
    not change projection identity (``projection.md`` § "Projection identity").
    A selection-policy change or a change to the exact resolved representative
    record identifiers also changes identity (Phase-4 § 27).

    The identity is a stable canonical string derived from these semantic
    inputs. It is not a figure-specific content digest of the prepared bytes.
    """

    figure_ref: str
    projection_semantics_version: int
    preparation_version: int
    artifact_ref: str
    record_id: str
    logical_contract: str
    scope: str = SCOPE_RECORD
    record_ids: tuple[str, ...] | None = None
    selection: ResolvedFigureSelection | None = None

    def __str__(self) -> str:
        payload: dict[str, object] = {
            "figure_ref": self.figure_ref,
            "projection_semantics_version": self.projection_semantics_version,
            "preparation_version": self.preparation_version,
            "artifact_ref": self.artifact_ref,
            "record_id": self.record_id,
            "scope": self.scope,
            "logical_contract": self.logical_contract,
        }
        if self.scope == SCOPE_ARTIFACT and self.record_ids is not None:
            payload["record_ids"] = list(self.record_ids)
        if self.selection is not None:
            payload["selection"] = self.selection.identity_input()
        return canonical_digest(payload)


__all__ = [
    "FigureProjection",
    "ProjectionIdentity",
    "ResolvedFigureSelection",
    "SourceRoleBinding",
]
