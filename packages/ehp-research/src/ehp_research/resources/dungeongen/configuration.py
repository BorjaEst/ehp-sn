from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from ehp_sn.configuration import BoundProducerConfiguration, ConfigurationSchema


@dataclass(frozen=True)
class Parameters:
    """The provider parameters of the external dungeon generator.

    These mirror the authored `[generator.params]` profile. The declaration is
    the complete supported surface; unknown or out-of-range values are rejected
    rather than defaulted silently during construction.
    """

    archetype: str
    size: str
    room_size_bias: float
    round_room_chance: float
    hall_chance: float
    density: float
    symmetry: str
    symmetry_break: float
    linearity: float
    loop_factor: float
    passage_width: int
    winding: float
    extra_room_connections: float
    extra_passage_junctions: float
    levels: int
    stair_frequency: float
    water_enabled: bool
    water_threshold: float


@dataclass(frozen=True)
class Configuration:
    """How the dungeongen provider is configured, independent of any request."""

    parameters: Parameters


def validate(config: Configuration) -> None:
    """Provider-specific constraints the declared model cannot express."""
    parameters = config.parameters

    if not 0.0 <= parameters.density <= 1.0:
        raise ValueError("parameters.density must be between 0 and 1.")

    if parameters.passage_width < 1:
        raise ValueError("parameters.passage_width must be positive.")


def resolve(document: BoundProducerConfiguration) -> Configuration:
    """Interpret the authored `[generator.params]` section into typed parameters.

    The framework owns ordinary decoding and validation; this hook only selects
    the provider-owned section, so the authored resource-profile form is
    preserved without repeating the declared model's fields here.
    """
    producer = document.producer
    generator = producer.get("generator")
    if not isinstance(generator, Mapping):
        raise ValueError("the resource profile must declare a [generator] section")

    raw_parameters = generator.get("params", {})
    if not isinstance(raw_parameters, Mapping):
        raise ValueError("the resource profile's [generator.params] must be a table")

    schema = ConfigurationSchema(model=Configuration, validate=validate)
    return schema.resolve(
        document=BoundProducerConfiguration(
            variant=document.variant,
            producer={"parameters": dict(raw_parameters)},
        )
    )


__all__ = ["Configuration", "Parameters", "resolve", "validate"]
