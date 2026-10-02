from __future__ import annotations

from ehp_sn import components, substrates
from ehp_sn.contracts.capabilities import raster_generator
from ehp_sn.contracts.data.structures.topology import raster_topology
from ehp_sn.requirements import (
    ONE,
    CapabilityFields,
    ContractCategory,
    RequestPolicy,
    Requirement,
    ResourceCategory,
)

from . import configuration, generation, inspection, planning, validation

_DESCRIPTION = (
    "Reusable procedural irregular raster-topology substrate: "
    "normalized raster topologies generated through the declared external "
    "generator integration and conforming to raster-topology/v1."
)

#: The consumer-local capability role Dungeon declares for raster generation.
GENERATOR_ROLE = "generator"


class Definition(substrates.Definition[configuration.Configuration, raster_topology.Artifact]):
    def resolve_configuration(
        self,
        *,
        document: substrates.BoundProducerConfiguration,
    ) -> configuration.Configuration:
        return configuration.resolve(
            document=document,
        )

    def plan(
        self,
        *,
        config: configuration.Configuration,
        dependencies: substrates.ResolvedDependencies,
    ) -> substrates.PlanningDeclaration:
        return planning.create(
            config=config,
            generator=dependencies.require(GENERATOR_ROLE, raster_generator.RasterGenerator).value,
        )

    def build(
        self,
        *,
        config: configuration.Configuration,
        dependencies: substrates.ResolvedDependencies,
    ) -> substrates.BuildResult[raster_topology.Artifact]:
        return generation.generate(
            config=config,
            generator=dependencies.require(GENERATOR_ROLE, raster_generator.RasterGenerator).value,
        )

    def validate(
        self,
        *,
        artifact: raster_topology.Artifact,
        level: substrates.ValidationLevel,
    ) -> substrates.ValidateResult:
        return validation.validate(
            artifact=artifact,
            level=level,
        )

    def summarize(
        self,
        *,
        artifact: raster_topology.Artifact,
    ) -> substrates.SummaryResult:
        return inspection.summarize(
            artifact=artifact,
        )

    def inspect(
        self,
        *,
        artifact: raster_topology.Artifact,
        record_id: str,
    ) -> substrates.InspectResult:
        return inspection.inspect(
            artifact=artifact,
            record_id=record_id,
        )


DEFINITION = Definition(
    ref=components.ComponentRef(kind="substrate", name="dungeon", version=1),
    description=_DESCRIPTION,
    requirements={
        GENERATOR_ROLE: Requirement(
            role=GENERATOR_ROLE,
            contract=raster_generator.V1,
            category=ContractCategory.CAPABILITY,
            cardinality=ONE,
            capability=CapabilityFields(
                resource_category=ResourceCategory.NONE,
                request_policy=RequestPolicy.ALLOWED,
            ),
        ),
    },
    contract=raster_topology.V1,
)


__all__ = ["DEFINITION"]
