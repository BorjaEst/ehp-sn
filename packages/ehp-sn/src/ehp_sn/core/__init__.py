from __future__ import annotations

import abc

from ehp_sn import components


class Definition(abc.ABC):
    """A registered, reusable scientific definition."""

    def __init__(
        self,
        *,
        ref: components.ComponentRef,
        description: str,
        contract: str | None = None,
    ) -> None:
        self.ref = ref
        self.description = description
        self.contract = contract

    @property
    def name(self) -> str:
        return self.ref.name


__all__ = [
    "Definition",
]
