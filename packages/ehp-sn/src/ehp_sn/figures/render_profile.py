"""Explicit resolved presentation policy (``RenderProfile``) for figure realization.

This module makes presentation policy explicit and versioned, replacing implicit
or ambient presentation behavior (Phase-4 · P4-T2). It implements the
non-scientific presentation-policy half of the realization boundary defined by
``docs/docs/framework/figures/rendering.md`` § "RenderProfile".

A :class:`RenderProfile` owns only presentation:

```text
physical figure width and height
margins
font family / font sizes
line-width defaults
marker-size defaults
panel-label presentation
background policy
non-semantic visual defaults
```

It must **not** own anything that changes the scientific view:

```text
source identity
cell / episode IDs
selection policy
scientific metric
checkpoint / split
scientific normalization
scientific value domain
scientifically meaningful colormap mapping
PanelSpec scientific meaning
```

Those belong to projection semantics (`projection.md`) and scientific visual
semantics (`visual-semantics.md`).

A public abstraction is justified here because presentation-policy identity is
an independent input to ``RealizationIdentity`` (``rendering.md`` §
``RealizationIdentity``): it must be resolvable, versioned, and must never leak
into ``ProjectionIdentity``. The profile is therefore provisional
(``api_stability: provisional``) — it exists to enforce the presentation versus
projection identity boundary, not to stabilize a full style language.

## Effective presentation configuration

The realization path resolves an effective rc-parameter configuration from the
selected :class:`RenderProfile` and applies it within a temporary Matplotlib
``rc_context`` (``rendering.md`` § "Matplotlib state isolation"). Presentation
values are never applied globally; they affect only the figure being realized.
"""

from __future__ import annotations

from dataclasses import dataclass

from ehp_sn.digests import canonical_digest


class PresentationError(ValueError):
    """A controlled presentation-resolution failure.

    Raised when presentation resolution cannot produce a valid effective
    configuration — for example when a presentation input conflicts with a
    scientifically protected visual-semantics value and must fail explicitly
    rather than silently reinterpret scientific meaning (Phase-4 · P4-T11).
    """


@dataclass(frozen=True, slots=True)
class ResolvedPresentation:
    """The fully resolved effective presentation configuration for one realization.

    This is the single state from which both rendering inputs and
    ``RealizationIdentity`` derive (Phase-4 · P4-T9/P4-T10). It holds the
    authoritative effective ``rc``-parameter mapping produced by resolution:

    ```text
    figure visual/presentation defaults
            +
    RenderProfile
            +
    explicit framework overrides
            ↓
    ResolvedPresentation (effective rc)
    ```

    Both the concrete drawing path and presentation identity consume this same
    resolved state, so no second resolution may occur inside rendering or
    serialization. ``profile`` records which authored profile produced it
    (informational provenance); only the effective ``rc`` values are
    identity-bearing.
    """

    rc: dict[str, object]
    profile: RenderProfile | None = None

    def identity_input(self) -> object:
        """The canonical effective-presentation identity value.

        Computed from the resolved effective ``rc`` values only — never from a
        profile name/version alone, so any intentional presentation input that
        alters the effective configuration changes realization identity, while
        ambient (unresolved) Matplotlib state does not (Phase-4 · P4-T10).
        """
        return {
            "effective_rc": {key: value for key, value in self.rc.items()},
        }

    def identity(self) -> str:
        """Return the digest identity of the effective presentation state."""
        return canonical_digest(self.identity_input())


@dataclass(frozen=True, slots=True)
class RenderProfile:
    """Versioned, explicitly resolved non-scientific presentation policy.

    ``name`` identifies the medium/venue policy (for example ``inspection`` or
    ``publication``) and ``version`` its policy revision. The physical extent,
    margins, and typography defaults are presentation only; none of these
    participates in ``ProjectionIdentity`` (`rendering.md` § ``RenderProfile``).

    ``extra_rc_params`` carries any additional non-semantic Matplotlib rc-parameter
    defaults (for example ``lines.linewidth``, ``xtick.labelsize``). Values here
    are presentation and must not include identity-bearing serialization
    parameters (format, DPI), which belong to the serialization policy instead.
    """

    name: str
    version: int
    width_inches: float
    height_inches: float
    font_size: float = 10.0
    margins_default: str = "tight"
    line_width: float = 1.0
    marker_size: float = 6.0
    extra_rc_params: dict[str, object] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if not isinstance(self.extra_rc_params, dict):
            object.__setattr__(self, "extra_rc_params", {})

    def identity_input(self) -> object:
        """The canonical presentation-only identity value of this profile.

        Includes the profile reference/version and every resolved presentation
        value, so that two profiles differing in any presentation value have
        distinct realization identity (but identical projection identity).
        """
        return {
            "name": self.name,
            "version": self.version,
            "width_inches": self.width_inches,
            "height_inches": self.height_inches,
            "font_size": self.font_size,
            "margins_default": self.margins_default,
            "line_width": self.line_width,
            "marker_size": self.marker_size,
            "extra_rc_params": dict(self.extra_rc_params),
        }

    def identity(self) -> str:
        """Return the digest identity of this presentation policy."""
        return canonical_digest(self.identity_input())

    def to_rc_params(self) -> dict[str, object]:
        """Resolve this profile into an effective ``matplotlib`` rc-parameter dict.

        Returns a fresh dict mapping rc-parameter names to presentation values
        plus the profile's own ``extra_rc_params``. This is the controlled
        presentation configuration applied within a temporary ``rc_context``;
        it is never installed globally.
        """
        rc: dict[str, object] = {
            "figure.figsize": (self.width_inches, self.height_inches),
            "font.size": self.font_size,
            "lines.linewidth": self.line_width,
            "lines.markersize": self.marker_size,
        }
        rc.update(dict(self.extra_rc_params))
        return rc


def default_render_profile(name: str = "default", version: int = 1) -> RenderProfile:
    """Return the framework's default presentation policy.

    Used when a caller realizes a projection without an explicit profile. The
    default is deliberately presentation-only and versioned so its identity is
    stable and reproducible.
    """
    return RenderProfile(
        name=name,
        version=version,
        width_inches=6.0,
        height_inches=6.0,
    )


__all__ = [
    "PresentationError",
    "RenderProfile",
    "ResolvedPresentation",
    "default_render_profile",
]
