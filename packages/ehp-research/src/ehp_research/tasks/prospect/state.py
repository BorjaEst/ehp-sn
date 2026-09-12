from __future__ import annotations

from ehp_sn import execution
from ehp_sn.contracts.data.datasets.records import sample_dataset
from ehp_sn.contracts.data.states import execution_state

ROLE = "acquired_environment_state"
CONTRACT = execution_state.V1


def requirements(
    *,
    artifact: sample_dataset.Artifact,
) -> tuple[execution.StateRequirement, ...]:
    raise NotImplementedError


__all__ = ["CONTRACT", "ROLE", "requirements"]
