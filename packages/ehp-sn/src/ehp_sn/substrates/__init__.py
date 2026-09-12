from __future__ import annotations

from dataclasses import dataclass

from ehp_sn import components, configuration, core, planning


@dataclass(frozen=True)
class Configuration: ...


@dataclass(frozen=True)
class BuildResult: ...


@dataclass(frozen=True)
class ValidationLevel: ...


@dataclass(frozen=True)
class ValidateResult: ...


@dataclass(frozen=True)
class SummaryResult: ...


@dataclass(frozen=True)
class InspectResult: ...


@dataclass(frozen=True)
class Definition(core.Definition): ...


__all__ = [
    "BuildResult",
    "Configuration",
    "Definition",
    "InspectResult",
    "SummaryResult",
    "ValidateResult",
    "ValidationLevel",
]
