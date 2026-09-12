from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlanningDeclaration:
    """Resolved build-input identity for one planned release coordinate."""

    target: str
    build_input_identity: str
    details: tuple[tuple[str, str], ...] = ()


__all__ = [
    "PlanningDeclaration",
]
