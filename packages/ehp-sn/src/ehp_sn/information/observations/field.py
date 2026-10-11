from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike

from ...contracts.diagnostics import ContractViolation
from ...contracts.identity import ContractRef
from ..spatial.domain import GridDomain

OBSERVATION_FIELD_V1 = ContractRef(name="observation-field", version=1)


@dataclass(frozen=True, slots=True, kw_only=True)
class ObservationField:
    domain: GridDomain
    channels: Mapping[str, ArrayLike]


class ObservationFieldValidator:
    def validate(self, value: ObservationField) -> None:
        if not value.channels:
            raise ContractViolation(
                "an observation field must declare at least one channel",
                contract=OBSERVATION_FIELD_V1,
                rule="observation-field.channels.empty",
            )
        for name, channel in value.channels.items():
            if tuple(np.asarray(channel).shape) != tuple(value.domain.shape):
                raise ContractViolation(
                    "channel shape must match the declared domain",
                    contract=OBSERVATION_FIELD_V1,
                    rule="observation-field.channels.shape",
                    subject=name,
                )
