from __future__ import annotations

from ehp_sn import components, execution, tasks
from ehp_sn.contracts.data.datasets.records import sample_dataset
from ehp_sn.contracts.data.structures import observations, relations, topology
from ehp_sn.contracts.data.structures.observations import categorical_field
from ehp_sn.contracts.data.structures.relations import simple_digraph
from ehp_sn.contracts.data.structures.topology import raster_topology

from . import configuration, generation, inspection, planning, state, validation

_DESCRIPTION = (
    "Memory-conditioned spatial-semantic prospective routing task: "
    "route prediction from acquired environment-specific state while "
    "direct topology and complete observation placement are withheld "
    "from model execution."
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
            relations=sources.require(relations.ROLE),
        )

    def state_requirements(
        self,
        *,
        artifact: sample_dataset.Artifact,
    ) -> tuple[execution.StateRequirement, ...]:
        return state.requirements(
            artifact=artifact,
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
    ref=components.ComponentRef(kind="task", name="prospect", version=1),
    description=_DESCRIPTION,
    sources={
        topology.ROLE: raster_topology.V1,
        observations.ROLE: categorical_field.V1,
        relations.ROLE: simple_digraph.V1,
    },
    states={state.ROLE: state.CONTRACT},
    contract=sample_dataset.V1,
)


__all__ = ["DEFINITION"]
