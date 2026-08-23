"""Producer-owned Maze-ND planning declaration capability (Capability 6).

This module owns the Maze-ND side of the demonstrated planning boundary: it
exposes the registered ``substrate:maze-nd/v1`` definition's planning capability
to the generic framework orchestration, without the framework importing this
package or reading any Maze-ND configuration field.

:class:`MazeNDPlanningCapability` implements the framework-owned
:class:`~ehp_sn.planning.SubstratePlanningCapability` protocol. Its
:meth:`~MazeNDPlanningCapability.plan` resolves a generic loaded configuration
through :func:`ehp_research.substrates.maze_nd.configuration.resolve_configuration`
(Capability 5) and declares the generic planning inputs:

* the effective :class:`MazeNDConfiguration` (opaque to the framework);
* one generic :class:`~ehp_sn.planning.ResourceRequirement` expressing the
  upstream **source** the build depends on. The producer owns the meaning of the
  source requirement; the framework owns binding it to an exact logical
  reference. The producer declares the exact source reference it requires, the
  accepted extraction schema, and that the requirement is mandatory
  (cardinality ``one``);
* the family-specific identity-bearing scientific inputs declared by the
  authoritative specification ``docs/docs/research/substrates/maze-nd-v1.md``.

Expected output contract is **not** declared here: it is invariant for the
registered definition and is owned by the definition (``raster-topology/v1``);
the plan derives it from the definition so there is a single authority for it.
"""

from __future__ import annotations

from ehp_sn.configuration import LoadedConfiguration
from ehp_sn.planning import (
    CARDINALITY_ONE,
    IdentityInput,
    PlanningDeclaration,
    ResourceRequirement,
    SubstratePlanningCapability,
)

from .configuration import resolve_configuration

#: The canonical requirement reference for the Maze-ND upstream source.
_SOURCE_REQUIREMENT_REF = "requirement:substrate/maze-nd-source/v1"
#: The resource kind of the upstream source requirement.
_SOURCE_RESOURCE_KIND = "raw-source"

#: Canonical names of the identity-bearing scientific inputs declared by
#: ``maze-nd-v1.md`` § "Family-specific identity inputs", in a stable order.
#: The framework never interprets these; they are producer-owned WHAT-labels.
_IDENTITY_ORDER: tuple[str, ...] = (
    "specification_reference",
    "variant",
    "source_reference",
    "source_fingerprint",
    "source_schema",
    "source_selection_policy",
    "selection_before_dedup",
    "normalization_policy",
    "connectivity_policy",
    "deduplication_policy",
)


class MazeNDPlanningCapability(SubstratePlanningCapability):
    """Planning capability for the registered ``substrate:maze-nd/v1`` definition."""

    def plan(self, document: LoadedConfiguration) -> PlanningDeclaration:
        """Resolve ``document`` into a Maze-ND configuration and declare planning inputs."""
        configuration = resolve_configuration(document)

        source_requirement = ResourceRequirement(
            ref=_SOURCE_REQUIREMENT_REF,
            resource_kind=_SOURCE_RESOURCE_KIND,
            accepted_schema_ids=(configuration.source_schema,),
            cardinality=CARDINALITY_ONE,
            definition_resource_ref=configuration.source_reference,
            description="immutable upstream source for Maze-ND raster-topology extraction",
        )

        identity_values: dict[str, object] = {
            "specification_reference": "maze-nd/v1",
            "variant": configuration.variant,
            "source_reference": configuration.source_reference,
            "source_fingerprint": configuration.source_fingerprint,
            "source_schema": configuration.source_schema,
            "source_selection_policy": configuration.source_selection_policy,
            "selection_before_dedup": configuration.selection_before_dedup,
            "normalization_policy": configuration.normalization_policy,
            "connectivity_policy": configuration.connectivity_policy,
            "deduplication_policy": configuration.deduplication_policy,
        }
        identity_inputs = tuple(
            IdentityInput(name=name, value=identity_values[name]) for name in _IDENTITY_ORDER
        )

        return PlanningDeclaration(
            configuration=configuration,
            resources=(source_requirement,),
            identity_inputs=identity_inputs,
        )


__all__ = ["MazeNDPlanningCapability"]
