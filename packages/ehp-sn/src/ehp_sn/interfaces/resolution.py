from __future__ import annotations

from collections.abc import Sequence

from .bindings import InterfaceBinder, InterfaceBinding
from .requirements import ConsumerRequirements, ProducerCapabilities
from .transformations import TransformDefinition


class InterfaceResolver:
    def __init__(self, *, binder: InterfaceBinder | None = None) -> None:
        self._binder = binder or InterfaceBinder()

    def resolve(
        self,
        *,
        producer: ProducerCapabilities,
        consumer: ConsumerRequirements,
        transforms: Sequence[TransformDefinition],
    ) -> InterfaceBinding:
        provided = list(producer.provides)
        selected: str | None = None
        for definition in transforms:
            if definition.source in provided and definition.destination not in provided:
                provided.append(definition.destination)
                selected = definition.destination.name
        binding = self._binder.bind(
            producer=ProducerCapabilities(provides=tuple(provided), access=producer.access),
            consumer=consumer,
        )
        return InterfaceBinding(fields=binding.fields, transformation=selected)
