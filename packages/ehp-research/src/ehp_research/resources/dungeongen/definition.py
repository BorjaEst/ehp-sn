from __future__ import annotations

from ehp_sn import components, resources
from ehp_sn.configuration import BoundProducerConfiguration
from ehp_sn.contracts.capabilities import raster_generator

from . import configuration
from .configuration import Configuration
from .integration import create

_DESCRIPTION = "Configured raster-generation capability over the dungeongen integration."


class Definition(resources.CapabilityDefinition[Configuration, raster_generator.RasterGenerator]):
    """The Dungeongen resource declaration.

    It supplies the provider construction hook; the framework owns profile
    loading, backend execution, contract checking, lifetime, and identity.
    """

    def resolve_configuration(
        self,
        *,
        document: BoundProducerConfiguration,
    ) -> Configuration:
        return configuration.resolve(document=document)


DEFINITION = Definition(
    ref=components.ComponentRef(kind="resource", name="dungeongen", version=1),
    description=_DESCRIPTION,
    configuration=Configuration,
    contract=raster_generator.V1,
    backend=resources.PythonCapability(factory=create),
)


__all__ = ["DEFINITION"]
