from __future__ import annotations

from ehp_sn import components, substrates
from ehp_sn.contracts.data.structures.topology import raster_topology

from . import configuration, generation, inspection, planning, validation

_DESCRIPTION = (
    "Reusable raster maze-topology substrate: "
    "normalized raster topologies extracted from an authoritative external "
    "source and conforming to raster-topology/v1."
)


class Definition(substrates.Definition):
    def resolve_configuration(
        self,
        *,
        document: substrates.LoadedConfiguration,
    ) -> substrates.Configuration:
        return configuration.resolve(
            document=document,
        )

    def plan(
        self,
        *,
        config: substrates.Configuration,
    ) -> substrates.PlanningDeclaration:
        return planning.create(
            config=config,
        )

    def build(
        self,
        *,
        config: substrates.Configuration,
    ) -> substrates.BuildResult:
        return generation.generate(
            config=config,
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
    ref=components.ComponentRef(kind="substrate", name="maze-nd", version=1),
    description=_DESCRIPTION,
    contract=raster_topology.V1,
)


__all__ = ["DEFINITION"]
