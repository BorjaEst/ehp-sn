from __future__ import annotations

from ehp_sn import components, tasks
from ehp_sn.contracts.acquisition import maze_examples
from ehp_sn.contracts.data.datasets.records import sample_dataset
from ehp_sn.requirements import ONE, ContractCategory, Requirement

from . import configuration, generation, inspection, planning, validation

#: Consumer-local role for the authoritative benchmark examples.
EXAMPLES_ROLE = "examples"

_DESCRIPTION = (
    "Maze-hard task: "
    "full-observation static shortest-route prediction over a raster maze, "
    "with a single topology source and a single case role."
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
            examples=dependencies.require(EXAMPLES_ROLE, maze_examples.MazeExamples).value,
        )

    def build(
        self,
        *,
        config: configuration.Configuration,
        dependencies: tasks.ResolvedDependencies,
    ) -> tasks.BuildResult[sample_dataset.Artifact]:
        return generation.generate(
            config=config,
            examples=dependencies.require(EXAMPLES_ROLE, maze_examples.MazeExamples).value,
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
    ref=components.ComponentRef(kind="task", name="maze-hard", version=1),
    description=_DESCRIPTION,
    requirements={
        EXAMPLES_ROLE: Requirement(
            role=EXAMPLES_ROLE,
            contract=maze_examples.V1,
            category=ContractCategory.ACQUISITION,
            cardinality=ONE,
        ),
    },
    contract=sample_dataset.V1,
)


__all__ = ["DEFINITION"]
