from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from ..experiments.refs import ComponentRef


@dataclass(frozen=True, slots=True)
class ConfiguredAdapter:
    adapter: Any
    ref: ComponentRef
    config: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Binding:
    task: ComponentRef
    model: ComponentRef
    input_adapter: ConfiguredAdapter
    output_adapter: ConfiguredAdapter
