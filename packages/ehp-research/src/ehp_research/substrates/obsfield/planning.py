from __future__ import annotations

import hashlib
from collections.abc import Iterable
from dataclasses import dataclass

from ehp_sn import substrates

from .configuration import Configuration

SPEC_REF = "obsfield/v1"


@dataclass(frozen=True)
class PlanningDeclaration(substrates.PlanningDeclaration): ...


def create(config: Configuration) -> PlanningDeclaration:
    return PlanningDeclaration(
        target=SPEC_REF,
        build_input_identity=build_input_identity(config),
        details=_declaration_details(config),
    )


def build_input_identity(config: Configuration) -> str:
    """Identity of everything that determines this build, release excluded."""
    return _digest(_declaration_inputs(config))


def record_id(config: Configuration, realization_index: int) -> str:
    """Stable identity of one realization within one artifact."""
    return _digest(_record_inputs(config, realization_index))


def random_state_seed(config: Configuration, realization_index: int) -> int:
    """Random state for one realization.

    Derived only from this realization's own identity inputs, so raising the
    requested realization count cannot alter earlier records.
    """
    return _seed_from(_record_inputs(config, realization_index))


def _record_inputs(config: Configuration, realization_index: int) -> tuple[str, ...]:
    """`obsfield/v1` family-specific identity inputs of one realization."""
    ...


def _declaration_inputs(config: Configuration) -> tuple[str, ...]:
    """The record inputs plus the requested realization count."""
    ...


def _declaration_details(config: Configuration) -> tuple[tuple[str, str], ...]:
    """Human-facing summary of the resolved declaration."""
    ...


def _seed_from(inputs: tuple[str, ...]) -> int:
    """Derive an independent random state from ordered identity inputs."""
    ...


def _digest(parts: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update(part.encode("utf-8"))
        digest.update(b"\x00")
    return digest.hexdigest()


__all__ = [
    "SPEC_REF",
    "PlanningDeclaration",
    "build_input_identity",
    "create",
    "random_state_seed",
    "record_id",
]
