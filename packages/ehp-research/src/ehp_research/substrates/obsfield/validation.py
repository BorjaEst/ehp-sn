from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import substrates
from ehp_sn.contracts.data.structures.observations import categorical_field
from ehp_sn.contracts.data.structures.observations.categorical_field import Artifact

from .configuration import Configuration


@dataclass(frozen=True)
class ValidationLevel(substrates.ValidationLevel): ...


@dataclass(frozen=True)
class ValidateResult(substrates.ValidateResult): ...


def validate(artifact: Artifact, level: ValidationLevel) -> ValidateResult:
    """Validate a committed artifact against `categorical-field/v1` and `obsfield/v1`."""
    diagnostics = _artifact_diagnostics(artifact, level)
    return ValidateResult(ok=not diagnostics, diagnostics=tuple(diagnostics))


def _artifact_diagnostics(artifact: Artifact, level: ValidationLevel) -> list[str]:
    """Artifact-scope invariants, together with every record's own invariants."""
    ...


def _record_diagnostics(record: categorical_field.RectangularField, level: ValidationLevel) -> list[str]:
    """CF-REC-001..006 plus OF-REC-008 and OF-REC-009, for one record.

    Full validation invokes the shared `categorical-field/v1` checks in
    addition to the family-specific ones.
    """
    ...


__all__ = ["validate", "ValidationLevel", "ValidateResult"]
