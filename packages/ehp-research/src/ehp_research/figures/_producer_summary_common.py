"""Shared research-owned helpers for producer generation-summary figures (Phase 5).

These helpers are consumed only by the producer generation-summary
``FigureSpec``s in ``ehp_research.figures``. They convert a committed artifact's
producer-owned provenance/auxiliary/record-descriptor surfaces into
research-local values and perform the deterministic rank-based min/median/max
representative selection shared by the gallery figures.

The framework deliberately never interprets a producer value
(``ARCH-001``); only the producer-owned figure does. This module is the
research-owned interpretation layer. It is a private helper module: it is not
registered and exposes no ``FigureSpec``.
"""

from __future__ import annotations

from typing import Any, cast

from ehp_sn.contracts.domains import (
    rectangular_row_column_domain,
)
from ehp_sn.contracts.observations import (
    AnonymousVocabulary,
    CategoricalField,
    ExternalVocabulary,
    Vocabulary,
    categorical_field,
)
from ehp_sn.contracts.relations import SimpleDigraph, simple_digraph
from ehp_sn.execution import LogicalRecord, LogicalResource


def identity_inputs_to_dict(provenance: dict[str, Any] | None) -> dict[str, Any]:
    """Turn the provenance ``identity_inputs`` list into a ``{name: value}`` dict.

    Provenance persists ``identity_inputs`` as a list of ``{"name":..., "value":...}``
    objects in declaration order (``provenance.json``). This helper gives the
    research figure a direct name→value view without interpreting a value.
    """
    if not provenance:
        return {}
    raw = provenance.get("identity_inputs")
    if not isinstance(raw, (list, tuple)):
        return {}
    result: dict[str, Any] = {}
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        if isinstance(name, str):
            result[name] = entry.get("value")
    return result


def guard_producer_identity(
    inputs: dict[str, Any],
    expected_spec_ref: str,
    figure_ref: str,
) -> None:
    """Research-owned producer-identity guard for a generation-summary figure.

    Reads the committed provenance's ``specification_reference`` identity input
    and raises a controlled :class:`TypeError` when it does not equal the
    expected producer spec reference. A generation-summary figure is therefore
    never applied to a collection produced by a different producer family.
    """
    actual = inputs.get("specification_reference")
    if actual != expected_spec_ref:
        raise TypeError(
            f"{figure_ref} requires a producer release with "
            f"specification_reference {expected_spec_ref!r}; committed provenance "
            f"has {actual!r}"
        )


def find_auxiliary(source: Any, name: str) -> LogicalResource | None:
    """Return the auxiliary logical resource named ``name``, or ``None``."""
    for resource in source.auxiliary:
        if resource.name == name:
            return resource
    return None


def record_descriptor(record: LogicalRecord, name: str) -> Any:
    """Return the value of a record's descriptor ``name``, or ``None``.

    A record's ``descriptors`` is a tuple of ``IdentityInput(name, value)``
    objects carried opaquely by the framework.
    """
    for descriptor in record.descriptors:
        if descriptor.name == name:
            return descriptor.value
    return None


def select_min_median_max(ordered_ids: tuple[str, ...]) -> tuple[str, ...]:
    """Select the min/median/max identities from a descriptor-ordered ranking.

    ``ordered_ids`` is the deterministic total order produced by
    :func:`rank_candidates` (descriptor primary, stable record identity
    secondary). Returns the first (minimum), median, and last (maximum)
    identities. A collection with one record returns it alone; two records
    return the first and last; a smaller collection returns all of its records
    in the deterministic order (Phase-4 § 23).
    """
    if len(ordered_ids) <= 1:
        return ordered_ids
    if len(ordered_ids) == 2:
        return (ordered_ids[0], ordered_ids[-1])
    median_index = (len(ordered_ids) - 1) // 2
    return (ordered_ids[0], ordered_ids[median_index], ordered_ids[-1])


def reconstruct_simple_digraph(content: object) -> SimpleDigraph:
    """Reconstruct the authoritative ``simple-digraph/v1`` typed view.

    Reads only the contract's authoritative fields (``node_count`` + ``edges``)
    and delegates to the contract's own constructor (Phase-2 § 5) — never a
    producer or physical-storage detail.
    """
    if isinstance(content, SimpleDigraph):
        return content
    if not isinstance(content, dict):
        raise TypeError(
            f"dagflow generation-summary record content must be a typed "
            f"SimpleDigraph or its authoritative content projection; got "
            f"{type(content).__name__}"
        )
    raw_count = content.get("node_count")
    raw_edges = content.get("edges")
    if not isinstance(raw_count, int) or not isinstance(raw_edges, (list, tuple)):
        raise TypeError(
            "dagflow generation-summary record content is missing integer 'node_count' and/or 'edges'"
        )
    return simple_digraph(
        int(raw_count),
        tuple((int(s), int(t)) for s, t in raw_edges),  # type: ignore[misc]
    )


def _coerce_vocabulary(declaration: object) -> Vocabulary:
    """Reconstruct the contract ``Vocabulary`` from its authoritative declaration."""
    if not isinstance(declaration, dict):
        raise TypeError("categorical-field record content's 'vocabulary' must be a declaration mapping")
    kind = declaration.get("kind")
    cardinality = declaration.get("cardinality")
    if kind == "anonymous":
        identity = declaration.get("identity")
        if not isinstance(identity, str) or not identity:
            raise TypeError("anonymous vocabulary requires a non-empty string identity")
        return AnonymousVocabulary(identity=identity, cardinality=cast(int, cardinality))
    if kind == "external":
        ref = declaration.get("ref")
        identity = declaration.get("identity")
        if not isinstance(ref, str) or not ref:
            raise TypeError("external vocabulary requires a non-empty string ref")
        if not isinstance(identity, str) or not identity:
            raise TypeError("external vocabulary requires a resolved immutable identity")
        return ExternalVocabulary(ref=ref, identity=identity, cardinality=cast(int, cardinality))
    raise TypeError(f"unknown vocabulary kind {kind!r} (expected 'anonymous' or 'external')")


def reconstruct_categorical_field(content: object) -> CategoricalField:
    """Reconstruct the authoritative ``categorical-field/v1`` typed view.

    Reads only the contract's authoritative fields (``domain`` + ``vocabulary``
    + ``observation_id``) and delegates to the contract's own constructor
    (Phase-2 § 5).
    """
    if isinstance(content, CategoricalField):
        return content
    if not isinstance(content, dict):
        raise TypeError(
            f"categorical-field record content must be a typed CategoricalField "
            f"or its authoritative content projection; got {type(content).__name__}"
        )
    domain_decl = content.get("domain")
    vocabulary_decl = content.get("vocabulary")
    observation_id = content.get("observation_id")
    if not isinstance(domain_decl, dict) or not isinstance(vocabulary_decl, dict):
        raise TypeError("categorical-field record content is missing 'domain' and/or 'vocabulary'")
    if not isinstance(observation_id, (list, tuple)):
        raise TypeError(
            "categorical-field record content is missing 'observation_id' in canonical position order"
        )
    try:
        height = int(domain_decl["height"])
        width = int(domain_decl["width"])
    except (KeyError, TypeError, ValueError) as exc:
        raise TypeError("categorical-field domain declaration is missing integer height/width") from exc
    domain = rectangular_row_column_domain(height, width)
    vocabulary = _coerce_vocabulary(vocabulary_decl)
    return categorical_field(domain, vocabulary, list(observation_id))


__all__ = [
    "find_auxiliary",
    "guard_producer_identity",
    "identity_inputs_to_dict",
    "reconstruct_categorical_field",
    "reconstruct_simple_digraph",
    "record_descriptor",
    "select_min_median_max",
]
