"""The framework Binding abstraction and its concrete resolved value.

Per ``docs/docs/framework/components/binding.md`` and ``ARCH-006``, a concrete
Binding is embedded in the experiment declaration and is not an independently
registered/discoverable component. A resolved ``Binding`` is the composition of
one task, one model, one configured ``InputAdapter``, and one configured
``OutputAdapter`` (``BIND-001``).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from ..experiments.refs import ComponentRef


@dataclass(frozen=True, slots=True)
class ConfiguredAdapter:
    """A resolved adapter component plus its adapter-owned configuration.

    ``config`` carries only genuine adapter-owned transformation choices
    (``ADAPT-003``); endpoint-owned values and derived composition state are
    computed during resolution and are not stored as authored config.
    """

    adapter: Any
    ref: ComponentRef
    config: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Binding:
    """The resolved composition of one task, one model, one input adapter, one output adapter.

    Identified by the canonical references of its task, model, and configured
    adapters. Carries a scoped identity for provenance, subordinate to the
    experiment (``ARCH-006``).
    """

    task: ComponentRef
    model: ComponentRef
    input_adapter: ConfiguredAdapter
    output_adapter: ConfiguredAdapter
