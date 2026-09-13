from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from ..components import ComponentRef


@dataclass(frozen=True, slots=True)
class ConfiguredAdapter:
    adapter: Any
    ref: ComponentRef
    config: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ModelIOSpec:
    """Declarative reconciliation of the experiment's selected task and model interfaces.

    The experiment selects the task and the model; a ``ModelIOSpec`` holds only the
    configured ``InputAdapter`` and ``OutputAdapter`` that reconcile their declared
    interfaces (``MIO-001``). It therefore carries no task or model reference.

    ``v1`` admits exactly these two slots. Additional slots, adapter chains, and a
    target-side slot are not yet specified and must not be invented here.
    """

    input: ConfiguredAdapter
    output: ConfiguredAdapter


__all__ = ["ConfiguredAdapter", "ModelIOSpec"]
