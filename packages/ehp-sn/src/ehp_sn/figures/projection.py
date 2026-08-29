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
preparation semantics/version
prepared stable view
```

There is deliberately **no figure-specific selection field** in this first
slice (Phase-1 § 12 · P1-T10). Real authored versus resolved scientific selection
is first exercised in the later HPC validation slice.

``ProjectionIdentity`` is computed only from semantic/provenance inputs. It never
reads visual, defaults, Matplotlib, typography, dimensions, backend, or
serialization fields (Phase-1 § 12 · P1-T10; ``projection.md`` § "Projection
identity"). It is not a figure-specific content digest; existing EHP-SN identity
and canonical-digest mechanisms are reused for provenance values.
"""

from __future__ import annotations

from dataclasses import dataclass

from ehp_sn.digests import canonical_digest


@dataclass(frozen=True, slots=True)
class SourceRoleBinding:
    """The exact authoritative source bound to one figure role.

    ``role`` is the semantic role this source satisfies for the figure (for
    example ``topology``). The source identity fields are the exact committed
    artifact/resource and record identity that the parent operation resolved
    (Phase-1 § 9 · P1-T7): an exact record of a committed artifact, its logical
    contract, and its stable logical contents.
    """

    role: str
    artifact_ref: str
    record_id: str
    logical_contract: str
    content: object


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
    """

    figure_ref: str
    projection_semantics_version: int
    preparation_version: int
    source: SourceRoleBinding
    content: object

    def identity(self) -> ProjectionIdentity:
        """Compute the projection identity from semantic/provenance inputs only."""
        return ProjectionIdentity(
            figure_ref=self.figure_ref,
            projection_semantics_version=self.projection_semantics_version,
            preparation_version=self.preparation_version,
            artifact_ref=self.source.artifact_ref,
            record_id=self.source.record_id,
            logical_contract=self.source.logical_contract,
        )


@dataclass(frozen=True, slots=True)
class ProjectionIdentity:
    """A figure's exact semantic/provenance identity (Phase 1).

    Determined by projection-semantic inputs:

    ```text
    figure projection semantics (reference + version)
    preparation semantics/version
    exact authoritative source identities (artifact, record, logical contract)
    ```

    Changing any of these creates a new projection. Presentation-only changes
    (panel placement, physical size, typography, DPI, serialization format,
    style) do not change projection identity (``projection.md`` § "Projection
    identity").

    The identity is a stable canonical string derived from these semantic
    inputs. It is not a figure-specific content digest of the prepared bytes.
    """

    figure_ref: str
    projection_semantics_version: int
    preparation_version: int
    artifact_ref: str
    record_id: str
    logical_contract: str

    def __str__(self) -> str:
        return canonical_digest(
            {
                "figure_ref": self.figure_ref,
                "projection_semantics_version": self.projection_semantics_version,
                "preparation_version": self.preparation_version,
                "artifact_ref": self.artifact_ref,
                "record_id": self.record_id,
                "logical_contract": self.logical_contract,
            }
        )


__all__ = [
    "FigureProjection",
    "ProjectionIdentity",
    "SourceRoleBinding",
]
