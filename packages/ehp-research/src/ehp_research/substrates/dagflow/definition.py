from __future__ import annotations

from ehp_sn import components, substrates
from ehp_sn.contracts.data.structures.relations import simple_digraph

from . import configuration, generation, inspection, planning, validation

_DESCRIPTION = (
    "Reusable single-terminal directed-graph substrate: "
    "procedurally generated directed graphs conforming to simple-digraph/v1."
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
        artifact: simple_digraph.Artifact,
        level: substrates.ValidationLevel,
    ) -> substrates.ValidateResult:
        return validation.validate(
            artifact=artifact,
            level=level,
        )

    def summarize(
        self,
        *,
        artifact: simple_digraph.Artifact,
    ) -> substrates.SummaryResult:
        return inspection.summarize(
            artifact=artifact,
        )

    def inspect(
        self,
        *,
        artifact: simple_digraph.Artifact,
        record_id: str,
    ) -> substrates.InspectResult:
        return inspection.inspect(
            artifact=artifact,
            record_id=record_id,
        )


DEFINITION = Definition(
    ref=components.ComponentRef(kind="substrate", name="dagflow", version=1),
    description=_DESCRIPTION,
    contract=simple_digraph.V1,
)


__all__ = ["DEFINITION"]
