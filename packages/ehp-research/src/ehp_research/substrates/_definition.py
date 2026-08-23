"""Shared immutable value type for authoritative substrate definitions.

This module defines the *research-side* ``SubstrateDefinition`` value type used
to represent a reusable substrate family's authoritative discovery-level facts.

It is deliberately small and carries no lifecycle or execution semantics:
no producer, planner, builder, validator, or configuration hooks live here
(those are derived in later planning phases from the concrete families'
configuration implementations). Its purpose in this capability is only to give
each family a single authoritative object whose identity plus discovery
metadata — canonical reference, concise description, and normalized output
contract — can be registered into the generic framework registry.

The generic framework discovery surface (``ehp_sn.discovery``) remains the
registration and resolution authority and is not extended here. This type is a
*research-owned* representation of a reusable scientific building block.
"""

from __future__ import annotations

from dataclasses import dataclass

from ehp_sn.experiments import ComponentRef


@dataclass(frozen=True, slots=True)
class SubstrateDefinition:
    """Immutable authoritative definition of a substrate family.

    Carries only demonstrated discovery-level facts:

    * ``ref`` — the canonical component reference (``substrate:<name>/v<N>``);
    * ``description`` — a concise authoritative description of the substrate
      definition;
    * ``output_contract`` — the canonical schema reference of the shared
      logical contract the substrate produces (e.g. ``simple-digraph/v1``).

    The component ``kind`` is derived from ``ref.kind`` rather than stored
    independently, so there is no duplicated identity authority: the canonical
    reference remains the single source of ``kind`` / ``name`` / ``version``
    (``docs/docs/framework/references.md``).
    """

    ref: ComponentRef
    description: str
    output_contract: str

    @property
    def kind(self) -> str:
        """The component kind, derived from the canonical reference."""
        return self.ref.kind
