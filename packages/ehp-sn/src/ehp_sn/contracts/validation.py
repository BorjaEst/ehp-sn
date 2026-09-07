from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ehp_sn.contracts.data.structures.observations import (
    CategoricalField,
    CategoricalFieldError,
)
from ehp_sn.contracts.data.structures.relations import SimpleDigraph, SimpleDigraphError

from .data.structures.domains import (
    AmbientDomainError,
    RectangularRowColumnDomain,
    rectangular_row_column_domain,
)
from .data.structures.observations import categorical_field
from .data.structures.relations import simple_digraph
from .topology import RasterTopology, RasterTopologyError, raster_topology


class ContractValidationError(ValueError):
    def __init__(
        self,
        schema_ref: str,
        invariant: str,
        message: str,
    ) -> None:
        super().__init__(f"{schema_ref} {invariant}: {message}")
        self.schema_ref = schema_ref
        self.invariant = invariant
        self.message = message


def _require_only_keys(
    schema_ref: str,
    invariant: str,
    instance: Mapping[str, Any],
    allowed: frozenset[str],
    present: frozenset[str],
) -> None:
    present_but_invalid = sorted(present & instance.keys())
    if present_but_invalid:
        raise ContractValidationError(
            schema_ref,
            invariant,
            f"instance declares non-authoritative field(s) {present_but_invalid!r}; "
            f"authoritative fields are {sorted(allowed)}. No field alias is accepted.",
        )


def _require_authoritative_keys(
    schema_ref: str,
    invariant: str,
    instance: Mapping[str, Any],
    required: frozenset[str],
) -> None:
    missing = sorted(required - instance.keys())
    if missing:
        raise ContractValidationError(
            schema_ref,
            invariant,
            f"missing authoritative field(s) {missing!r}; got {sorted(instance.keys())}",
        )


def validate_extent_declaration(schema_ref: str, declaration: object) -> RectangularRowColumnDomain:
    if not isinstance(declaration, Mapping):
        raise ContractValidationError(
            schema_ref,
            "AD-REC-001",
            f"domain declaration must be a mapping, got {type(declaration).__name__}",
        )
    schema = declaration.get("schema")
    if schema != "rectangular-grid/v1":
        raise ContractValidationError(
            schema_ref,
            "AD-REC-002",
            f"expected registered domain schema 'rectangular-grid/v1', got {schema!r}",
        )
    try:
        height = int(declaration["height"])
        width = int(declaration["width"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ContractValidationError(
            schema_ref,
            "AD-REC-001",
            f"domain declaration is missing integer height/width: {exc}",
        ) from exc
    try:
        domain = rectangular_row_column_domain(height, width)
    except AmbientDomainError as exc:
        raise ContractValidationError(schema_ref, "AD-REC-001", str(exc)) from exc

    declared_count = declaration.get("position_count")
    if declared_count is not None and int(declared_count) != domain.position_count:
        raise ContractValidationError(
            schema_ref,
            "AD-REC-003",
            f"declared position_count {declared_count} != derived {domain.position_count}",
        )
    for field, expected in (
        ("coordinate_system", domain.coordinate_system),
        ("coordinate_structure", domain.coordinate_structure),
        ("shape", domain.shape),
    ):
        if field in declaration and declaration[field] != expected:
            raise ContractValidationError(
                schema_ref,
                "AD-REC-003",
                f"schema-determined field {field!r} is {declaration[field]!r}, expected {expected!r}",
            )
    return domain


def validate_simple_digraph(instance: Mapping[str, Any]) -> SimpleDigraph:
    schema_ref = "simple-digraph/v1"
    _require_authoritative_keys(schema_ref, "SG-REC-001", instance, frozenset({"node_count", "edges"}))

    _require_only_keys(
        schema_ref,
        "SG-REC-005",
        instance,
        frozenset({"node_count", "edges"}),
        frozenset(
            {
                "successor",
                "successors",
                "adjacency",
                "edges_2d",
                "transition",
            }
        ),
    )
    node_count = instance["node_count"]
    edges_raw = instance["edges"]
    if not isinstance(edges_raw, Sequence) or isinstance(edges_raw, (str, bytes)):
        raise ContractValidationError(
            schema_ref,
            "SG-REC-002",
            f"edges must be a sequence of pairs, got {type(edges_raw).__name__}",
        )
    edges: list[tuple[int, int]] = []
    for pair in edges_raw:
        if not isinstance(pair, Sequence) or isinstance(pair, (str, bytes)) or len(pair) != 2:
            raise ContractValidationError(
                schema_ref, "SG-REC-002", f"edge {pair!r} is not a (source, target) pair"
            )
        edges.append((int(pair[0]), int(pair[1])))
    graph = _from_constructor(schema_ref, simple_digraph, node_count, edges)

    _validate_materialized_derived_views(
        schema_ref,
        "SG-REC-006",
        instance,
        {
            "acyclic": graph.acyclic,
            "terminal_count": graph.terminal_count,
            "all_nodes_reach_a_terminal": graph.all_nodes_reach_a_terminal,
        },
    )
    return graph


def validate_raster_topology(instance: Mapping[str, Any]) -> RasterTopology:
    schema_ref = "raster-topology/v1"
    _require_authoritative_keys(schema_ref, "RT-REC-001", instance, frozenset({"extent", "passable"}))

    _require_only_keys(
        schema_ref,
        "RT-REC-001",
        instance,
        frozenset({"extent", "passable"}),
        frozenset({"domain"}),
    )
    extent = validate_extent_declaration(schema_ref, instance["extent"])
    passable = instance["passable"]
    if not isinstance(passable, Sequence) or isinstance(passable, (str, bytes)):
        raise ContractValidationError(
            schema_ref,
            "RT-REC-002",
            f"passable must be a sequence of booleans, got {type(passable).__name__}",
        )
    topology = _from_constructor(schema_ref, raster_topology, extent, list(passable))

    _validate_materialized_derived_views(
        schema_ref,
        "RT-REC-007",
        instance,
        {
            "state_count": topology.state_count,
            "component_count": topology.component_count,
            "connected": topology.connected,
        },
    )
    return topology


def validate_categorical_field(instance: Mapping[str, Any]) -> CategoricalField:
    schema_ref = "categorical-field/v1"
    _require_authoritative_keys(
        schema_ref, "CF-REC-001", instance, frozenset({"domain", "vocabulary", "observation_id"})
    )

    _require_only_keys(
        schema_ref,
        "CF-REC-001",
        instance,
        frozenset({"domain", "vocabulary", "observation_id"}),
        frozenset({"extent"}),
    )

    _require_only_keys(
        schema_ref,
        "CF-REC-006",
        instance,
        frozenset({"domain", "vocabulary", "observation_id"}),
        frozenset(
            {
                "topology_record_id",
                "topology",
                "topology_ref",
                "parent_topology",
                "state_to_position",
                "position_to_state",
                "next_state",
                "topology_schema",
            }
        ),
    )
    domain = validate_extent_declaration(schema_ref, instance["domain"])
    vocabulary = _coerce_vocabulary(schema_ref, instance["vocabulary"])
    observation_id = instance["observation_id"]
    if not isinstance(observation_id, Sequence) or isinstance(observation_id, (str, bytes)):
        raise ContractValidationError(
            schema_ref,
            "CF-REC-002",
            "observation_id must be a sequence of categorical integers, "
            f"got {type(observation_id).__name__}",
        )
    return _from_constructor(schema_ref, categorical_field, domain, vocabulary, list(observation_id))


def _coerce_vocabulary(schema_ref: str, declaration: object):
    from .data.structures.observations import AnonymousVocabulary, ExternalVocabulary

    if not isinstance(declaration, Mapping):
        raise ContractValidationError(
            schema_ref,
            "CF-REC-005",
            f"vocabulary declaration must be a mapping, got {type(declaration).__name__}",
        )
    kind = declaration.get("kind")
    if kind == "anonymous":
        identity = declaration.get("identity")
        if not isinstance(identity, str) or not identity:
            raise ContractValidationError(
                schema_ref, "CF-REC-005", "anonymous vocabulary requires a non-empty string identity"
            )
        return AnonymousVocabulary(
            identity=identity, cardinality=_coerce_cardinality(schema_ref, declaration)
        )
    if kind == "external":
        ref = declaration.get("ref")
        identity = declaration.get("identity")
        if not isinstance(ref, str) or not ref:
            raise ContractValidationError(
                schema_ref, "CF-REC-005", "external vocabulary requires a non-empty string ref"
            )
        if not isinstance(identity, str) or not identity:
            raise ContractValidationError(
                schema_ref, "CF-REC-005", "external vocabulary requires a resolved immutable identity"
            )
        return ExternalVocabulary(
            ref=ref,
            identity=identity,
            cardinality=_coerce_cardinality(schema_ref, declaration),
        )
    raise ContractValidationError(
        schema_ref,
        "CF-REC-005",
        f"unknown vocabulary kind {kind!r} (expected 'anonymous' or 'external')",
    )


def _coerce_cardinality(schema_ref: str, declaration: Mapping[str, Any]) -> int:
    cardinality = declaration.get("cardinality")
    if not isinstance(cardinality, int) or isinstance(cardinality, bool) or cardinality < 1:
        raise ContractValidationError(
            schema_ref,
            "CF-REC-005",
            f"vocabulary cardinality must be an integer >= 1, got {cardinality!r}",
        )
    return cardinality


def _from_constructor(schema_ref: str, constructor: Any, *args: Any) -> Any:
    try:
        return constructor(*args)
    except (RasterTopologyError, SimpleDigraphError, CategoricalFieldError, AmbientDomainError) as exc:
        raise ContractValidationError(schema_ref, "invariant", str(exc)) from exc


def _validate_materialized_derived_views(
    schema_ref: str,
    invariant: str,
    instance: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> None:
    for field, value in expected.items():
        if field in instance and instance[field] != value:
            raise ContractValidationError(
                schema_ref,
                invariant,
                f"materialized derived field {field!r} is {instance[field]!r}, "
                f"expected {value!r} from authoritative content",
            )


__all__ = [
    "ContractValidationError",
    "validate_categorical_field",
    "validate_extent_declaration",
    "validate_raster_topology",
    "validate_simple_digraph",
]
