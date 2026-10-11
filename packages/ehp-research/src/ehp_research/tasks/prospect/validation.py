from __future__ import annotations

from ehp_sn import ContractRef, ContractViolation

from .definition import ProspectTaskDefinition
from .settings import ProspectSettings

PROSPECT_V1 = ContractRef(name="prospect", version=1)


class ProspectSettingsValidator:
    def validate(self, value: ProspectSettings) -> None:
        if value.context_length < 1:
            raise ContractViolation(
                "context_length must be at least 1",
                contract=PROSPECT_V1,
                rule="prospect.parameter.context_length",
                subject="context_length",
            )
        if value.prediction_horizon < 1:
            raise ContractViolation(
                "prediction_horizon must be at least 1",
                contract=PROSPECT_V1,
                rule="prospect.parameter.prediction_horizon",
                subject="prediction_horizon",
            )
        if not value.memory_mode:
            raise ContractViolation(
                "prospect must declare a memory mode",
                contract=PROSPECT_V1,
                rule="prospect.parameter.memory_mode",
                subject="memory_mode",
            )


class ProspectInformationAccessValidator:
    def validate(self, value: ProspectTaskDefinition) -> None:
        if not value.acquisition_policy:
            raise ContractViolation(
                "prospect must declare an acquisition policy",
                contract=PROSPECT_V1,
                rule="prospect.access.acquisition_policy",
                subject="acquisition_policy",
            )
        if not value.query_policy:
            raise ContractViolation(
                "prospect must declare a query policy",
                contract=PROSPECT_V1,
                rule="prospect.access.query_policy",
                subject="query_policy",
            )
        if value.acquisition_policy == value.query_policy:
            raise ContractViolation(
                "acquisition and query phases must remain distinguishable",
                contract=PROSPECT_V1,
                rule="prospect.access.phase_distinct",
            )


class ProspectDatasetValidator:
    def validate(self, value: object) -> None:
        if not hasattr(value, "__len__"):
            raise ContractViolation(
                "a prospect dataset must be indexable",
                contract=PROSPECT_V1,
                rule="prospect.dataset.indexed",
            )
