"""Authoritative ObsField v1 substrate definition.

This module is the single authoritative home of the ``substrate:obsfield/v1``
definition object (``OBSFIELD_DEFINITION``) at the discovery level in
``ehp_research``.

It carries only demonstrated discovery facts:

* canonical reference: ``substrate:obsfield/v1``;
* a concise description of the substrate definition;
* the normalized output contract: ``categorical-field/v1``.

The scientific specification for ObsField v1 is
``docs/docs/research/substrates/obsfield-v1.md``.
"""

from __future__ import annotations

from ehp_sn.experiments import ComponentRef

from .._definition import SubstrateDefinition

OBSFIELD_DEFINITION = SubstrateDefinition(
    ref=ComponentRef.parse("substrate:obsfield/v1"),
    description=(
        "Reusable categorical observation-field substrate: procedurally "
        "generated persistent categorical fields conforming to "
        "categorical-field/v1, independent of topology."
    ),
    output_contract="categorical-field/v1",
)

__all__ = ["OBSFIELD_DEFINITION"]
