"""Authoritative Dagflow v1 substrate definition.

This module is the single authoritative home of the ``substrate:dagflow/v1``
definition object (``DAGFLOW_DEFINITION``) at the discovery level in
``ehp_research``.

It carries only demonstrated discovery facts:

* canonical reference: ``substrate:dagflow/v1``;
* a concise description of the substrate definition;
* the normalized output contract: ``simple-digraph/v1``.

It deliberately carries no generation, configuration, or planning semantics
(pending the planning phase), and no producer/execution hooks. The scientific
specification for Dagflow v1 is
``docs/docs/research/substrates/dagflow-v1.md``.
"""

from __future__ import annotations

from ehp_sn.experiments import ComponentRef

from .._definition import SubstrateDefinition

DAGFLOW_DEFINITION = SubstrateDefinition(
    ref=ComponentRef.parse("substrate:dagflow/v1"),
    description=(
        "Reusable single-terminal directed-graph substrate: procedurally "
        "generated directed graphs conforming to simple-digraph/v1."
    ),
    output_contract="simple-digraph/v1",
)

__all__ = ["DAGFLOW_DEFINITION"]
