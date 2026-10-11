from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ContractValidator[T](Protocol):
    def validate(self, value: T) -> None: ...


@runtime_checkable
class CompatibilityValidator[T](Protocol):
    def validate(self, values: T) -> None: ...


def validate_contract[T](value: T, *, validator: ContractValidator[T]) -> None:
    validator.validate(value)
