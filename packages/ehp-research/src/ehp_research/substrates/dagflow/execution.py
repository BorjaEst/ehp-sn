"""Dagflow execution operation (producer integration).

This module owns the *producer execution operation* for the registered
``substrate:dagflow/v1`` definition: the research-side callable bound to the
definition through the framework execution composition. It consumes the
authoritative, opaque producer-effective configuration from the framework-owned
:class:`~ehp_sn.execution.MaterializationSession`, performs only producer-owned
scientific production semantics (graph generation and intrinsic split
membership), and hands identity-neutral graph records through the framework's
``GeneratedRecordBody`` / materialization boundary.

The producer never performs framework-owned lifecycle work: it does not load
configuration, plan, reselect resources, derive ``record_id``, construct
manifests, fingerprint, allocate releases, handle reuse/conflict, publish, or
project the CLI. The framework derives the resulting ``record_id`` from the
producer-declared realization key.
"""

from __future__ import annotations

from ehp_sn.contracts.relations import SimpleDigraph
from ehp_sn.execution import GeneratedRecordBody, MaterializationSession, RealizationKey
from ehp_sn.planning import IdentityInput

from .configuration import DagflowConfiguration
from .generation import generate_artifact_records


def _content(graph: SimpleDigraph) -> dict[str, object]:
    """Return the JSON-compatible canonical labelled content of a graph record.

    The authoritative scientific payload is ``node_count`` plus the canonical
    simple directed edge relation (``simple-digraph/v1`` labelled-graph
    equality). It is expressed as a JSON-compatible structure so the framework
    can canonicalize it for logical-resource digests without reading producer
    types.
    """
    return {
        "node_count": graph.node_count,
        "edges": [[source, target] for source, target in graph.edges],
    }


def _realization_key(
    config: DagflowConfiguration,
    split: str,
    realization_index: int,
) -> RealizationKey:
    """Declare the producer-owned canonical realization identity for one record.

    These are family-specific semantic inputs the framework never interprets; it
    only canonicalizes them into the framework-derived ``record_id``. They
    uniquely identify the intended realization while remaining stable when
    requested counts increase (no total-count dependence).
    """
    return RealizationKey(
        inputs=(
            IdentityInput("specification_reference", "dagflow/v1"),
            IdentityInput("variant", config.variant),
            IdentityInput("generation_protocol", config.generation_protocol),
            IdentityInput("seed", config.seed),
            IdentityInput("split", split),
            IdentityInput("realization_index", realization_index),
        )
    )


def execute(session: MaterializationSession) -> None:
    """Execute the Dagflow producer operation against the framework session.

    Reads the opaque :class:`DagflowConfiguration` from the authoritative
    session, generates the complete artifact record collection (graph content
    plus intrinsic split), and materializes each record through the framework's
    ``GeneratedRecordBody`` boundary so the framework derives the ``record_id``.

    The producer may supply split membership, generation descriptors, and
    realization-identity inputs; it never supplies ``record_id``, artifact ID,
    release, or final path.
    """
    configuration = session.configuration
    if not isinstance(configuration, DagflowConfiguration):
        raise TypeError(f"expected DagflowConfiguration, got {type(configuration).__name__}")

    for split, realization_index, graph in generate_artifact_records(configuration):
        session.add_record(
            GeneratedRecordBody(
                content=_content(graph),
                realization_key=_realization_key(configuration, split, realization_index),
                descriptors=(IdentityInput("split", split),),
            )
        )


__all__ = ["execute"]
