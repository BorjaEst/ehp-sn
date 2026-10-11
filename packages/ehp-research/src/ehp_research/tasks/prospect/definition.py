from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class ProspectTaskDefinition:
    information: object
    acquisition_policy: str
    query_policy: str
