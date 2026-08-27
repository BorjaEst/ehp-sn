"""Framework-owned release-coordinate resolution for a substrate build.

This module resolves the *intended committed release coordinate* of a resolved
substrate build from framework artifact semantics alone:

```text
family
variant
release
    ↓
data/interim/<family>/<variant>/v<release>/
```

The release number is **selected at the invocation layer** (``--release N``),
which is retained as the canonical authority. It is never auto-assigned:
``data-layout.md`` § "Release numbering" states *"The framework does not
auto-assign the next release."* and ``data-artifacts.md`` § "Version source and
overrides" states *"The framework must not auto-assign the next release
number."* Therefore the framework never invents ``max(existing)+1``; it
resolves the exact coordinate the caller selects. A ``release`` value declared
in the effective configuration is accepted only as a **legacy compatibility
fallback** (deprecated in favor of the invocation-layer selection), never as the
canonical location.

The producer never supplies the physical path and never learns the coordinate.

The coordinate is derived from:

* ``family`` — the producer family, taken from the resolved component reference
  (``plan.target.name``);
* ``variant`` — the producer-declared canonical ``variant`` identity input
  (e.g. ``single-terminal``); all substrate producers declare it as a canonical
  identity input, so it is a framework-read of a producer-declared canonical
  value, never an interpretation of a producer configuration field;
* ``release`` — a framework-owned artifact-coordinate value selected at the
  invocation layer (``--release N``), with a config-declared value accepted only
  as a legacy fallback.

The physical placement convention belongs to the monorepo workspace
(``data-artifacts.md`` § "Conventional release coordinates"); this module
yields the coordinate, and the caller supplies the physical artifact root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ReleaseCoordinate:
    """The intended committed release coordinate of a resolved substrate build.

    Identifies ``<family>/<variant>/v<release>`` — the logical coordinate under
    ``data/interim/`` (or the equivalent configured physical root). It is the
    sole framework-owned authority for release placement: the producer never
    supplies it and the CLI never invents it.
    """

    family: str
    variant: str
    release: int

    @property
    def version(self) -> str:
        """The human-facing ``v<release>`` coordinate segment."""
        return f"v{self.release}"

    def relative_path(self) -> tuple[str, str, str]:
        """Return the coordinate segments ``(family, variant, v<release>)``."""
        return (self.family, self.variant, self.version)

    @property
    def name(self) -> str:
        """The reference ``name`` segment (``<family>/<variant>``)."""
        return f"{self.family}/{self.variant}"


#: The canonical identity-input name under which substrate producers declare
#: their consumer-visible structural variant.
_VARIANT_INPUT = "variant"

#: The legacy framework-owned configuration key that may declare the release
#: number. This is a framework artifact-coordinate field, not a producer
#: scientific field, and is accepted only as a temporary compatibility fallback
#: (deprecated in favor of the invocation-layer ``--release`` selection).
_RELEASE_KEY = "release"


class ReleaseCoordinateResolutionError(Exception):
    """The intended release coordinate could not be resolved from a build.

    Raised when a required coordinate component is absent: the producer family
    is unknown, the producer declares no canonical ``variant`` identity input,
    or the effective configuration declares no framework-owned ``release``
    value. It is a framework-domain error, not a CLI category; the CLI maps it
    at its own layer.
    """


def resolve_release_coordinate(
    *,
    family: str,
    variant: str | None,
    release: int | None,
) -> ReleaseCoordinate:
    """Resolve a validated release coordinate from framework semantics.

    ``family`` is the producer family; ``variant`` the producer-declared variant
    (or ``None`` when the producer declares none); ``release`` the
    invocation-layer release selection (``--release N``), or a config-declared
    value accepted only as a legacy fallback (``None`` when absent).

    The framework does **not** auto-assign a missing release: a missing value is
    a resolution failure, never an implicit ``max(existing)+1``.
    """
    if not family:
        raise ReleaseCoordinateResolutionError("cannot resolve release coordinate: empty family")
    if variant is None:
        raise ReleaseCoordinateResolutionError(
            "cannot resolve release coordinate: producer declares no canonical 'variant' identity input"
        )
    if release is None:
        raise ReleaseCoordinateResolutionError(
            "cannot resolve release coordinate: no release number is selected; "
            "provide --release N (a config-declared value is only a legacy "
            "fallback); the framework does not auto-assign release numbers"
        )
    if release < 1:
        raise ReleaseCoordinateResolutionError(
            f"cannot resolve release coordinate: release number must be a positive "
            f"integer, got {release!r}"
        )
    return ReleaseCoordinate(family=family, variant=variant, release=release)


def variant_from_identity_inputs(
    identity_inputs: Any,
) -> str | None:
    """Return the producer-declared ``variant`` identity input value, or ``None``.

    Reads the canonical producer-declared ``variant`` input from a plan's
    identity-input sequence. This is a framework read of a producer-declared
    canonical value (all substrate producers declare ``variant``), never an
    interpretation of a producer configuration field.
    """
    for item in identity_inputs:
        if item.name == _VARIANT_INPUT:
            return str(item.value)
    return None


def release_from_config(values: Any) -> int | None:
    """Return the legacy config-declared release number in ``values``, or ``None``.

    Reads the framework artifact-coordinate ``release`` scalar from the generic
    loaded configuration document. This is a framework artifact-coordinate read
    (the release number is a framework concern, per ``data-artifacts.md``
    "Version source and overrides"); it is not an interpretation of producer
    scientific configuration. Because the invocation-layer ``--release`` is the
    canonical source, a value found here is accepted only as a legacy
    compatibility fallback.
    """
    value = values.get(_RELEASE_KEY) if isinstance(values, dict) else None
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ReleaseCoordinateResolutionError(f"configured release must be an integer, got {value!r}")
    return value


__all__ = [
    "ReleaseCoordinate",
    "ReleaseCoordinateResolutionError",
    "release_from_config",
    "resolve_release_coordinate",
    "variant_from_identity_inputs",
]
