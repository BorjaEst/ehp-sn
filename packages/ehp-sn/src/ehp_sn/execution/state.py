from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import artifacts
from ehp_sn.contracts.data.states import execution as execution_state


@dataclass(frozen=True)
class StateRequirement:
    role: str
    contract: str
    context_id: str


@dataclass(frozen=True)
class ResolvedStateRequirement: ...


@dataclass(frozen=True)
class StateKey: ...


def derive_state_key(
    requirement: ResolvedStateRequirement,
) -> StateKey:
    raise NotImplementedError


__all__ = ["ResolvedStateRequirement", "StateKey", "StateRequirement", "derive_state_key"]
