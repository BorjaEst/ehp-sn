from __future__ import annotations

from ..contracts.diagnostics import ContractViolation
from ..contracts.identity import ContractRef
from .records import EpisodeRecord
from .schema import DatasetSchema
from .sequential import SEQUENTIAL_EPISODES_V1

DATASET_SCHEMA_V1 = ContractRef(name="dataset-schema", version=1)


class EpisodeValidator:
    def validate(self, value: EpisodeRecord) -> None:
        if not value.observations:
            raise ContractViolation(
                "an episode must contain at least one observation",
                contract=SEQUENTIAL_EPISODES_V1,
                rule="sequential-episodes.observations.empty",
            )
        if len(value.actions) != len(value.observations) - 1:
            raise ContractViolation(
                "an episode has T+1 observations and T actions",
                contract=SEQUENTIAL_EPISODES_V1,
                rule="sequential-episodes.episode.alignment",
            )


class DatasetSchemaValidator:
    def validate(self, value: DatasetSchema) -> None:
        if not value.inputs:
            raise ContractViolation(
                "a dataset schema must declare at least one input",
                contract=DATASET_SCHEMA_V1,
                rule="dataset-schema.inputs.empty",
            )
        overlap = set(value.inputs) & set(value.targets)
        if overlap:
            raise ContractViolation(
                "inputs and targets must not share field names",
                contract=DATASET_SCHEMA_V1,
                rule="dataset-schema.names.disjoint",
                subject=str(sorted(overlap)),
            )
