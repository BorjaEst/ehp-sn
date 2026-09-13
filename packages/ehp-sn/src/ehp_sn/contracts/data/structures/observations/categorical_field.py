from __future__ import annotations

from dataclasses import dataclass

from ehp_sn.contracts.data.structures import domains

from . import _core

SCHEMA_REF = "categorical-field"
V1 = f"{SCHEMA_REF}/v1"


@dataclass(frozen=True)
class CategoricalField(_core.Observations):
    """A categorical observation field defined over an ambient domain.

    Domain geometry is composed, not inherited: the field *is* a member of the
    observations family and *has* an ambient domain drawn from the registered
    domain alternatives. Domain kinds are not encoded as field subclasses.
    """

    record_id: str
    domain: domains.Domain


@dataclass(frozen=True)
class Artifact:
    """Minimal container for committed categorical-field records."""

    records: tuple[CategoricalField, ...] = ()


__all__ = [
    "SCHEMA_REF",
    "V1",
    "Artifact",
    "CategoricalField",
]
