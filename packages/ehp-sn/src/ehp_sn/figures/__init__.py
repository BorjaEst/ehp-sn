"""EHP-SN framework figures.

This package implements the generic executable figure capability defined by
``docs/docs/framework/figures/`` and the cross-cutting figure invariants
``FIG-001`` through ``FIG-004`` in ``docs/invariants.md``.

Phase 1 is a bootstrap figure walking skeleton: it proves one exact committed
record satisfying a framework-owned logical contract can be resolved as a figure
source, matched to a canonical ``FigureSpec`` through the ordinary component
catalogue, projected with explicit provenance, and realized directly as a
Matplotlib figure — without producer-specific logic, parallel figure
infrastructure, or presentation leakage into projection identity.

This package is framework-owned (``ARCH-001``): it imports no concrete research
package and contains no concrete experiment composition. Reusable scientific
figure meaning belongs to ``ehp_research`` or experiment-local figure
specifications in later phases.
"""

from __future__ import annotations

from .contracts import (
    FIGURE_KIND,
    FigureInputCompatibilityError,
    FigureInputRequirement,
    FigureSpec,
)
from .persistence import FigureContentIntegrityError, verify_content_digest
from .projection import (
    FigureProjection,
    ProjectionIdentity,
    ResolvedFigureSelection,
    SourceRoleBinding,
)
from .providers import (
    FIGURE_PROVIDER_ENTRY_POINT_GROUP,
    effective_figure_registry,
    register_builtin_figures,
    register_installed_figure_providers,
)
from .realization import (
    ContentDigest,
    RealizationError,
    RealizationIdentity,
    RealizedFigure,
    RenderingEnvironmentProvenance,
    ResolvedFigureRealization,
    realize_projection,
    record_rendering_environment,
    resolve_figure_realization,
)
from .render_profile import (
    PresentationError,
    RenderProfile,
    ResolvedPresentation,
    default_render_profile,
)
from .serialization import (
    FORMAT_PNG,
    FORMAT_SVG,
    ResolvedSerializationPolicy,
    SerializationError,
    resolve_serialization_policy,
)
from .service import (
    FigureResult,
    FigureServiceError,
    UnknownFigureError,
    inspect_figure,
    prepare_figure,
    render_figure_projection,
)

__all__ = [
    "ContentDigest",
    "FIGURE_KIND",
    "FIGURE_PROVIDER_ENTRY_POINT_GROUP",
    "FORMAT_PNG",
    "FORMAT_SVG",
    "FigureContentIntegrityError",
    "FigureInputCompatibilityError",
    "FigureInputRequirement",
    "FigureProjection",
    "FigureResult",
    "FigureServiceError",
    "FigureSpec",
    "PresentationError",
    "ProjectionIdentity",
    "RealizationError",
    "RealizationIdentity",
    "RealizedFigure",
    "RenderProfile",
    "RenderingEnvironmentProvenance",
    "ResolvedFigureRealization",
    "ResolvedFigureSelection",
    "ResolvedPresentation",
    "ResolvedSerializationPolicy",
    "SerializationError",
    "SourceRoleBinding",
    "UnknownFigureError",
    "default_render_profile",
    "effective_figure_registry",
    "inspect_figure",
    "prepare_figure",
    "realize_projection",
    "record_rendering_environment",
    "register_builtin_figures",
    "register_installed_figure_providers",
    "render_figure_projection",
    "resolve_figure_realization",
    "resolve_serialization_policy",
    "verify_content_digest",
]
