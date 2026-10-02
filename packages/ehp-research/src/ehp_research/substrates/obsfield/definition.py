from __future__ import annotations

from ehp_sn import components, substrates
from ehp_sn.contracts.data.structures.observations import categorical_field

from . import configuration, generation, inspection, planning, validation

_DESCRIPTION = (
    "Reusable categorical observation-field substrate: "
    "procedurally generated persistent categorical fields conforming to "
    "categorical-field/v1, independent of topology."
)


class Definition(substrates.Definition[configuration.Configuration, categorical_field.Artifact]):
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
        )

    def build(
        self,
        *,
        config: configuration.Configuration,
        dependencies: substrates.ResolvedDependencies,
    ) -> substrates.BuildResult[categorical_field.Artifact]:
        return generation.generate(
            config=config,
        )

    def validate(
        self,
        *,
        artifact: categorical_field.Artifact,
        level: substrates.ValidationLevel,
    ) -> substrates.ValidateResult:
        return validation.validate(
            artifact=artifact,
            level=level,
        )

    def summarize(
        self,
        *,
        artifact: categorical_field.Artifact,
    ) -> substrates.SummaryResult:
        return inspection.summarize(
            artifact=artifact,
        )

    def inspect(
        self,
        *,
        artifact: categorical_field.Artifact,
        record_id: str,
    ) -> substrates.InspectResult:
        return inspection.inspect(
            artifact=artifact,
            record_id=record_id,
        )


DEFINITION = Definition(
    ref=components.ComponentRef(kind="substrate", name="obsfield", version=1),
    description=_DESCRIPTION,
    contract=categorical_field.V1,
)


__all__ = ["DEFINITION"]
