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

from .api import (
    FigureSource,
    prepare_figure,
    realize_projection,
    render_figure,
    render_figure_projection,
)
from .contracts import (
    FIGURE_KIND,
    FigureInputCompatibilityError,
    FigureInputRequirement,
    FigureSpec,
    InspectionCapacityExceeded,
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
    record_rendering_environment,
    resolve_figure_realization,
)
from .render_profile import (
    PresentationError,
    RenderProfile,
    ResolvedPresentation,
    default_render_profile,
)
from .scope import SCOPE_ARTIFACT, SCOPE_RECORD, SOURCE_SCOPES
from .serialization import (
    FORMAT_PNG,
    FORMAT_SVG,
    ResolvedSerializationPolicy,
    SerializationError,
    resolve_serialization_policy,
)
from .service import (
    AUTO_FIGURE_TOKEN,
    AmbiguousFigureError,
    FigureResult,
    FigureServiceError,
    NoCompatibleFigureError,
    UnknownFigureError,
    inspect_artifact_figure,
    inspect_figure,
    list_compatible_figures,
    list_figures_for_artifact,
    list_figures_for_record,
    resolve_auto_figure,
)
from .source import (
    ARTIFACT_METADATA_SURFACES,
    SURFACE_AUXILIARY,
    SURFACE_PRODUCER_DESCRIPTORS,
    SURFACE_PROVENANCE,
    ArtifactSourceContent,
)

__all__ = [
    "AUTO_FIGURE_TOKEN",
    "AmbiguousFigureError",
    "ARTIFACT_METADATA_SURFACES",
    "ArtifactSourceContent",
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
    "FigureSource",
    "FigureSpec",
    "InspectionCapacityExceeded",
    "NoCompatibleFigureError",
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
    "SCOPE_ARTIFACT",
    "SCOPE_RECORD",
    "SOURCE_SCOPES",
    "SURFACE_AUXILIARY",
    "SURFACE_PRODUCER_DESCRIPTORS",
    "SURFACE_PROVENANCE",
    "SerializationError",
    "SourceRoleBinding",
    "UnknownFigureError",
    "default_render_profile",
    "effective_figure_registry",
    "inspect_artifact_figure",
    "inspect_figure",
    "list_compatible_figures",
    "list_figures_for_artifact",
    "list_figures_for_record",
    "prepare_figure",
    "realize_projection",
    "record_rendering_environment",
    "register_builtin_figures",
    "register_installed_figure_providers",
    "render_figure",
    "render_figure_projection",
    "resolve_auto_figure",
    "resolve_figure_realization",
    "resolve_serialization_policy",
    "verify_content_digest",
]
