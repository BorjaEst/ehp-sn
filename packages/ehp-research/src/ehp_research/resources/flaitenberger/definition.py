from __future__ import annotations

from ehp_sn import components, resources
from ehp_sn.configuration import BoundProducerConfiguration
from ehp_sn.contracts.acquisition import maze_examples

from . import configuration
from .configuration import Configuration
from .decoding import decode

_DESCRIPTION = "Acquisition of authoritative maze examples from the flaitenberger dataset."


class Definition(resources.AcquisitionDefinition[Configuration, maze_examples.MazeExamples]):
    """The Flaitenberger acquisition declaration.

    It supplies the decoder hook; the framework owns locating, downloading,
    verifying, and exposing the exact input.
    """

    def resolve_configuration(
        self,
        *,
        document: BoundProducerConfiguration,
    ) -> Configuration:
        return configuration.resolve(document=document)


DEFINITION = Definition(
    ref=components.ComponentRef(kind="resource", name="flaitenberger", version=1),
    description=_DESCRIPTION,
    configuration=Configuration,
    contract=maze_examples.V1,
    backend=resources.HuggingFaceSnapshot(
        configuration_section="dataset",
        decoder=decode,
    ),
)


__all__ = ["DEFINITION"]
