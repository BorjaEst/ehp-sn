"""Explicit resolved serialization policy for figure realization.

This module makes serialization policy explicit and fully resolved before any
Matplotlib serialization begins (Phase-4 · P4-T3). It implements the
serialization-request and policy-resolved half of the realization boundary
defined by ``docs/docs/framework/figures/rendering.md`` § "Serialization
request".

Serialization must **not** depend on implicit Matplotlib, filename, environment,
or ``rcParams`` defaults. No identity-affecting serialization parameter may be
silently inferred from:

```text
filename extension
ambient rcParams
Matplotlib defaults
provider-local save logic
```

## Presentation / serialization boundary

The authority is EHP-SN semantics, not the backend API shape (``rendering.md``
§ "Presentation/serialization boundary"). For example:

```text
physical extent      → presentation (RenderProfile)
background / padding → presentation
format               → serialization
raster DPI           → serialization
format-specific encoding parameters → serialization
```

The first supported formats are only those required by concrete consumers. Phase 4
validates one raster format (PNG) and one vector format (SVG); PDF is added only
when a real consumer requires it.
"""

from __future__ import annotations

from dataclasses import dataclass

from ehp_sn.digests import canonical_digest

#: Raster serialization format validated by Phase 4 (``rendering.md`` § "Serialization request").
FORMAT_PNG = "png"

#: Vector serialization format validated by Phase 4.
FORMAT_SVG = "svg"

#: The formats currently supported by the centralized serialization path.
SUPPORTED_FORMATS: frozenset[str] = frozenset({FORMAT_PNG, FORMAT_SVG})


class SerializationError(ValueError):
    """A controlled figure-serialization failure.

    Raised when a serialization request references an unsupported format or
    carries an unrecognized realization-affecting parameter. It is a controlled
    realization failure, never a raw Matplotlib save error leaking through.
    """


@dataclass(frozen=True, slots=True)
class ResolvedSerializationPolicy:
    """The fully resolved serialization policy for one realization.

    Constructed from an authored request after default/policy resolution, so
    that by the time Matplotlib serialization begins every identity-affecting
    serialization parameter is explicit.

    ``format`` is the target serialization format (``png`` or ``svg``); ``dpi``
    is the raster resolution applied when relevant; ``metadata_policy`` is a
    small, explicit policy marker for whether non-visual serialization metadata
    is emitted (informational, not a scientific value). ``extra_parameters``
    carries any additional explicit, realization-affecting, format-specific
    encoding parameters (for example ``bbox_inches`` / ``transparent``).

    Neither ``format`` nor any parameter here is ever inferred from a filename
    extension or from ambient Matplotlib state.
    """

    format: str
    dpi: int = 100
    metadata_policy: str = "none"
    extra_parameters: dict[str, object] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.format not in SUPPORTED_FORMATS:
            raise SerializationError(
                f"unsupported serialization format {self.format!r}; supported: "
                f"{sorted(SUPPORTED_FORMATS)}"
            )
        if not isinstance(self.dpi, int) or self.dpi <= 0:
            raise SerializationError(f"invalid serialization DPI {self.dpi!r}; must be a positive int")
        if not isinstance(self.extra_parameters, dict):
            object.__setattr__(self, "extra_parameters", {})

    def identity_input(self) -> object:
        """The canonical identity-relevant value of this serialization policy.

        Includes only **visual** realization-affecting serialization parameters
        (format, DPI, format-specific encoding). Non-visual file metadata
        (``metadata_policy``, output path, resource name, timestamps, author
        metadata) is deliberately **not** part of realization identity
        (Phase-4 · P4-T12): a metadata change must not change
        ``RealizationIdentity``.
        """
        return {
            "format": self.format,
            "dpi": self.dpi,
            "extra_parameters": dict(self.extra_parameters),
        }

    def identity(self) -> str:
        """Return the digest identity of this resolved serialization policy."""
        return canonical_digest(self.identity_input())

    def validate(self) -> None:
        """Validate the resolved policy before Matplotlib is invoked (P4-T15).

        Ensures the DPI is a positive integer and that no extra parameter key
        silently shadows a framework-owned serialization attribute. Invalid
        values raise :class:`SerializationError` so a semantically invalid
        request fails through a controlled framework error before drawing or
        serialization, rather than surfacing as a backend error.
        """
        if not isinstance(self.dpi, int) or self.dpi <= 0:
            raise SerializationError(f"invalid serialization DPI {self.dpi!r}; must be a positive int")
        for key in ("format", "dpi", "metadata_policy"):
            if key in self.extra_parameters:
                raise SerializationError(
                    f"serialization parameter {key!r} is framework-owned and must not appear "
                    "in extra_parameters"
                )


def resolve_serialization_policy(
    *,
    format: str,
    dpi: int | None = None,
    metadata_policy: str | None = None,
    extra_parameters: dict[str, object] | None = None,
) -> ResolvedSerializationPolicy:
    """Resolve an authored serialization request into a fully explicit policy.

    Defaults for values that are not identity-bearing are applied here, so that
    the returned policy is completely resolved before serialization. The format
    is mandatory and never defaults/inferred. DPI defaults only as a
    realization convenience and is recorded explicitly in the resolved policy
    so it can participate in identity when it affects the realization.

    Raises :class:`SerializationError` for an unsupported format.
    """
    return ResolvedSerializationPolicy(
        format=format,
        dpi=100 if dpi is None else dpi,
        metadata_policy="none" if metadata_policy is None else metadata_policy,
        extra_parameters=dict(extra_parameters or {}),
    )


__all__ = [
    "FORMAT_PNG",
    "FORMAT_SVG",
    "SUPPORTED_FORMATS",
    "ResolvedSerializationPolicy",
    "SerializationError",
    "resolve_serialization_policy",
]
