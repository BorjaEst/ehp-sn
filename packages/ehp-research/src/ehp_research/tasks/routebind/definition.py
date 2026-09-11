from __future__ import annotations

from ehp_sn import components, tasks
from ehp_sn.contracts.data.datasets.records import sample_dataset
from ehp_sn.contracts.data.structures import observations, relations, topology
from ehp_sn.contracts.data.structures.observations import categorical_field
from ehp_sn.contracts.data.structures.relations import simple_digraph
from ehp_sn.contracts.data.structures.topology import raster_topology

from . import configuration, generation, inspection, planning, validation

_DESCRIPTION = (
    "Fully observed spatial-semantic prospective routing task: "
    "visible spatial structure and observation placement under a hidden "
    "corpus-level semantic transition law."
)


class Definition(tasks.Definition):
    def resolve_configuration(
        self,
        *,
        document: tasks.LoadedConfiguration,
    ) -> tasks.Configuration:
        return configuration.resolve(
            document=document,
        )

    def plan(
        self,
        *,
        config: tasks.Configuration,
        sources: tasks.ResolvedSources,
    ) -> tasks.PlanningDeclaration:
        return planning.create(
            config=config,
            topology=sources.require(topology.ROLE),
            observation=sources.require(observations.ROLE),
            relations=sources.require(relations.ROLE),
        )

    def build(
        self,
        *,
        config: tasks.Configuration,
        sources: tasks.ResolvedSources,
    ) -> tasks.BuildResult:
        return generation.generate(
            config=config,
            topology=sources.require(topology.ROLE),
            observation=sources.require(observations.ROLE),
            semantic_graph_source=sources.require(relations.ROLE),
        )

    def validate(
        self,
        *,
        artifact: sample_dataset.Artifact,
        level: tasks.ValidationLevel,
    ) -> tasks.ValidateResult:
        return validation.validate(
            artifact=artifact,
            level=level,
        )

    def summarize(
        self,
        *,
        artifact: sample_dataset.Artifact,
    ) -> tasks.SummaryResult:
        return inspection.summarize(
            artifact=artifact,
        )

    def inspect(
        self,
        *,
        artifact: sample_dataset.Artifact,
        record_id: str,
    ) -> tasks.InspectResult:
        return inspection.inspect(
            artifact=artifact,
            record_id=record_id,
        )


DEFINITION = Definition(
    ref=components.ComponentRef(kind="task", name="routebind", version=1),
    description=_DESCRIPTION,
    sources={
        topology.ROLE: raster_topology.V1,
        observations.ROLE: categorical_field.V1,
        relations.ROLE: simple_digraph.V1,
    },
    contract=sample_dataset.V1,
)


__all__ = ["DEFINITION"]
