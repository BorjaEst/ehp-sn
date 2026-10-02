from __future__ import annotations

from ehp_sn import components, tasks
from ehp_sn.artifacts import ArtifactRef
from ehp_sn.contracts.data.datasets.records import sample_dataset
from ehp_sn.contracts.data.structures.observations import categorical_field
from ehp_sn.contracts.data.structures.relations import simple_digraph
from ehp_sn.contracts.data.structures.topology import raster_topology
from ehp_sn.requirements import ONE, ContractCategory, Requirement

from . import configuration, generation, inspection, planning, validation

#: Consumer-local roles. Prospect owns these; the contracts do not.
TOPOLOGY_ROLE = "topology"
OBSERVATION_ROLE = "observation"
RELATIONS_ROLE = "relations"

_DESCRIPTION = (
    "Memory-conditioned spatial-semantic prospective routing task: "
    "route prediction from acquired environment-specific state while "
    "direct topology and complete observation placement are withheld "
    "from model execution."
)


class Definition(
    tasks.Definition[
        configuration.Configuration,
        sample_dataset.Artifact,
    ]
):
    def resolve_configuration(
        self,
        *,
        document: tasks.BoundProducerConfiguration,
    ) -> configuration.Configuration:
        return configuration.resolve(
            document=document,
        )

    def plan(
        self,
        *,
        config: configuration.Configuration,
        dependencies: tasks.ResolvedDependencies,
    ) -> tasks.PlanningDeclaration:
        return planning.create(
            config=config,
            topology=dependencies.require(TOPOLOGY_ROLE, ArtifactRef).value,
            observation=dependencies.require(OBSERVATION_ROLE, ArtifactRef).value,
            relations=dependencies.require(RELATIONS_ROLE, ArtifactRef).value,
        )

    def build(
        self,
        *,
        config: configuration.Configuration,
        dependencies: tasks.ResolvedDependencies,
    ) -> tasks.BuildResult[sample_dataset.Artifact]:
        return generation.generate(
            config=config,
            topology=dependencies.require(TOPOLOGY_ROLE, ArtifactRef).value,
            observation=dependencies.require(OBSERVATION_ROLE, ArtifactRef).value,
            relations=dependencies.require(RELATIONS_ROLE, ArtifactRef).value,
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
    requirements={
        TOPOLOGY_ROLE: Requirement(
            role=TOPOLOGY_ROLE,
            contract=raster_topology.V1,
            category=ContractCategory.CONTENT,
            cardinality=ONE,
        ),
        OBSERVATION_ROLE: Requirement(
            role=OBSERVATION_ROLE,
            contract=categorical_field.V1,
            category=ContractCategory.CONTENT,
            cardinality=ONE,
        ),
        RELATIONS_ROLE: Requirement(
            role=RELATIONS_ROLE,
            contract=simple_digraph.V1,
            category=ContractCategory.CONTENT,
            cardinality=ONE,
        ),
    },
    contract=sample_dataset.V1,
)


__all__ = ["DEFINITION"]
