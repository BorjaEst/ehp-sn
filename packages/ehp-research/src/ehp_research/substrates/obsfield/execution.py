"""ObsField execution operation (producer integration).

This module owns the *producer execution operation* for the registered
``substrate:obsfield/v1`` definition: the research-side callable bound to the
definition through the framework execution composition. It consumes the
authoritative, opaque producer-effective configuration from the framework-owned
:class:`~ehp_sn.execution.MaterializationSession`, performs only producer-owned
scientific production semantics (observation assignment over the complete
ambient domain), and hands identity-neutral field records through the
framework's ``GeneratedRecordBody`` / materialization boundary.

The producer never performs framework-owned lifecycle work. ObsField defines no
intrinsic split, and the record schema is ``categorical-field/v1``.
"""

from __future__ import annotations

from ehp_sn.contracts.observations import CategoricalField
from ehp_sn.execution import GeneratedRecordBody, MaterializationSession, RealizationKey
from ehp_sn.planning import IdentityInput

from .configuration import ObsFieldConfiguration
from .generation import generate_realizations


def _content(field: CategoricalField) -> dict[str, object]:
    """Return the JSON-compatible canonical content of a field record.

    The authoritative scientific payload is the domain declaration, the
    vocabulary declaration, and the observation assignment (``categorical-field/v1``
    content equality). It is JSON-compatible so the framework can canonicalize it
    for logical-resource digests without reading producer types.
    """
    return {
        "domain": field.domain.declaration(),
        "vocabulary": field.vocabulary.declaration(),
        "observation_ids": list(field.observation_ids),
    }


def _realization_key(config: ObsFieldConfiguration, realization_index: int) -> RealizationKey:
    """Declare the producer-owned canonical realization identity for one record.

    ObsField carries no intrinsic split; the realization index plus the resolved
    semantic identity uniquely identify one intended realization.
    """
    return RealizationKey(
        inputs=(
            IdentityInput("specification_reference", "obsfield/v1"),
            IdentityInput("variant", config.variant),
            IdentityInput("assignment_protocol", config.assignment_protocol),
            IdentityInput("vocabulary_identity", config.vocabulary_identity),
            IdentityInput("seed", config.seed),
            IdentityInput("realization_index", realization_index),
        )
    )


def execute(session: MaterializationSession) -> None:
    """Execute the ObsField producer operation against the framework session.

    Reads the opaque :class:`ObsFieldConfiguration`, generates the complete
    realization collection over the ambient domain, and materializes each field
    through the framework's ``GeneratedRecordBody`` boundary. No topology,
    passability, or split is ever required.
    """
    configuration = session.configuration
    if not isinstance(configuration, ObsFieldConfiguration):
        raise TypeError(f"expected ObsFieldConfiguration, got {type(configuration).__name__}")

    for index, field in enumerate(generate_realizations(configuration)):
        session.add_record(
            GeneratedRecordBody(
                content=_content(field),
                realization_key=_realization_key(configuration, index),
                descriptors=(),
            )
        )


__all__ = ["execute"]
