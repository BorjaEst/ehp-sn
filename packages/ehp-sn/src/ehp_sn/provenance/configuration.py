from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from ..contracts.identity import ContractRef


@dataclass(frozen=True, slots=True, kw_only=True)
class ConfigurationEvidence:
    contract: ContractRef
    values: Mapping[str, object]
