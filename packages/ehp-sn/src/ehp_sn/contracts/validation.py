"""Framework-owned shared contract validation (Phase 1 · canonical conformance).

This module is the **one framework authority** for validating the *declared
logical instance* of each shared logical schema against its normative
``* /v1`` contract, and it is the boundary that makes normal loading
non-repairing (``docs/invariants.md`` ARCH-014; Phase 1 § 8–9, § 19).

The required interpretation path is:

```text
committed resource
        ↓  lossless physical decoding  (read the content dict verbatim)
declared logical instance   (a JSON-ish dict)
        ↓  shared contract validation  (this module)
validated shared logical record
```

Decoding is deliberately not performed here: :mod:`ehp_sn.artifacts.resolve`
already reads a committed record's ``content`` verbatim (lossless). This module
validates that decoded declared logical instance and returns a validated typed
record, or raises an explicit contract-domain error.

Three things it does, and which map onto the phase requirements:

* **Lossless-decoding boundary enforcement** — it accepts only the
  authoritative field keys for each schema. A `raster-topology/v1` instance
  containing `domain` instead of `extent` is rejected (not silently repaired),
  and a `categorical-field/v1` instance containing `extent` instead of
  `domain` is rejected. This implements the negative schema-drift requirement
  (Phase 1 § 34) and prevents a loader from making non-conforming input
  conforming (Phase 1 § 8, "Never" block).
* **Single validation authority** — each validator reconstructs the typed
  record through the owning contract constructor, which enforces every
  ``*-REC-*`` invariant from the authoritative content. It does not reimplement
  any invariant (Phase 1 § 25: producer duplicated shared invariants = 0).
* **Materialized derived-view agreement** — when a declared instance also
  stores a canonical derived view, the validator verifies it agrees exactly
  with the value derived from authoritative content (Phase 1 § 19). It never
  trusts an independently materialized derived view as authoritative.

Each validator raises a :class:`ContractValidationError` identifying the
schema, the violated invariant, and the observed versus expected value, so a
caller can translate it into a controlled conformance failure rather than a raw
exception leak.

Producer validators (in ``ehp_research``) must invoke these shared validators
and add only producer-owned invariants; they must not reimplement a shared
invariant (Phase 1 § 25).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .domains import (
    AmbientDomainError,
    RectangularRowColumnDomain,
    rectangular_row_column_domain,
)
from .observations import CategoricalField, CategoricalFieldError, categorical_field
from .relations import SimpleDigraph, SimpleDigraphError, simple_digraph
from .topology import RasterTopology, RasterTopologyError, raster_topology


class ContractValidationError(ValueError):
    """A declared logical instance does not conform to its shared contract.

    Raised by the shared validators when a decoded declared logical instance
    violates a ``*-REC-*`` invariant, includes an alias/legacy field instead of
    the authoritative one, or stores a derived view that disagrees with
    authoritative content. This is a contract-domain (framework-owned) error,
    not a producer error.
    """

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
    """Reject a declared instance that carries a non-authoritative field.

    ``present`` lists the non-authoritative keys that would previously have
    been tolerated as aliases and that this boundary must reject. This is the
    silent-repair prevention: an instance declaring the wrong field is invalid
    current-schema content, not a migration candidate.
    """
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


# ---------------------------------------------------------------------------
# ambient-domain/v1 (AD-REC-001..003)
# ---------------------------------------------------------------------------


def validate_extent_declaration(schema_ref: str, declaration: object) -> RectangularRowColumnDomain:
    """Reconstruct and validate a ``rectangular-row-column/v1`` domain declaration.

    Validates ``AD-REC-001`` (complete dense position reconstruction), the
    registered schema identity (``AD-REC-002``), and schema-determined versus
    derived field agreement (``AD-REC-003``). Returns the validated
    :class:`~ehp_sn.contracts.domains.RectangularRowColumnDomain`.
    """
    if not isinstance(declaration, Mapping):
        raise ContractValidationError(
            schema_ref,
            "AD-REC-001",
            f"domain declaration must be a mapping, got {type(declaration).__name__}",
        )
    schema = declaration.get("schema")
    if schema != "rectangular-row-column/v1":
        raise ContractValidationError(
            schema_ref,
            "AD-REC-002",
            f"expected registered domain schema 'rectangular-row-column/v1', got {schema!r}",
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
    # AD-REC-003 — schema-determined and derived declaration fields must agree.
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


# ---------------------------------------------------------------------------
# simple-digraph/v1 (SG-REC-001..006)
# ---------------------------------------------------------------------------


def validate_simple_digraph(instance: Mapping[str, Any]) -> SimpleDigraph:
    """Validate a declared ``simple-digraph/v1`` logical instance.

    Accepts the authoritative fields ``node_count`` and ``edges``, rejects any
    alias representation (for example a ``successor`` table is not accepted as
    an alias for ``edges``), reconstructs the typed
    :class:`~ehp_sn.contracts.relations.SimpleDigraph` through the owning
    constructor (which enforces ``SG-REC-001..006``), and — when a materialized
    derived view is present — verifies it agrees with authoritative content
    (``SG-REC-006``).
    """
    schema_ref = "simple-digraph/v1"
    _require_authoritative_keys(schema_ref, "SG-REC-001", instance, frozenset({"node_count", "edges"}))
    # Negative drift: a successor table is not an alias for edges.
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


# ---------------------------------------------------------------------------
# raster-topology/v1 (RT-REC-001..007)
# ---------------------------------------------------------------------------


def validate_raster_topology(instance: Mapping[str, Any]) -> RasterTopology:
    """Validate a declared ``raster-topology/v1`` logical instance.

    Accepts the authoritative fields ``extent`` (a complete
    ``rectangular-row-column/v1`` declaration) and ``passable``. Rejects a
    ``domain`` alias (the historical raster field name is *not* accepted as an
    alias for ``extent``; that is invalid current-schema content), reconstructs
    the typed :class:`~ehp_sn.contracts.topology.RasterTopology` through the
    owning constructor (which enforces ``RT-REC-001..007`` under the fixed
    grid4/undirected/unit/no-stay parameters), and verifies any materialized
    derived view agrees with authoritative content.
    """
    schema_ref = "raster-topology/v1"
    _require_authoritative_keys(schema_ref, "RT-REC-001", instance, frozenset({"extent", "passable"}))
    # Negative drift: the historical raster `domain` field is not `extent`.
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


# ---------------------------------------------------------------------------
# categorical-field/v1 (CF-REC-001..006)
# ---------------------------------------------------------------------------


def validate_categorical_field(instance: Mapping[str, Any]) -> CategoricalField:
    """Validate a declared ``categorical-field/v1`` logical instance.

    Accepts the authoritative fields ``domain``, ``vocabulary``, and
    ``observation_id``. Rejects a topology-parent reference and a ``extent``
    alias for ``domain`` (``CF-REC-001``/``CF-REC-006``), reconstructs the typed
    :class:`~ehp_sn.contracts.observations.CategoricalField` through the owning
    constructor (which enforces ``CF-REC-001..005``), and rejects any topology
    reference (``CF-REC-006``).
    """
    schema_ref = "categorical-field/v1"
    _require_authoritative_keys(
        schema_ref, "CF-REC-001", instance, frozenset({"domain", "vocabulary", "observation_id"})
    )
    # Negative drift: a categorical field contains `domain`, never `extent`.
    _require_only_keys(
        schema_ref,
        "CF-REC-001",
        instance,
        frozenset({"domain", "vocabulary", "observation_id"}),
        frozenset({"extent"}),
    )
    # CF-REC-006 — no topology parent / state-mapping / schema reference.
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
    """Coerce a vocabulary declaration into a resolved contract Vocabulary.

    Supports the anonymous and external vocabulary logical forms per
    ``categorical-field/v1`` § "Vocabulary contract", reconstructing the
    type through the owning types rather than a parallel parser.
    """
    from .observations import AnonymousVocabulary, ExternalVocabulary

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


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------


def _coerce_cardinality(schema_ref: str, declaration: Mapping[str, Any]) -> int:
    """Validate and return the vocabulary cardinality as a positive integer."""
    cardinality = declaration.get("cardinality")
    if not isinstance(cardinality, int) or isinstance(cardinality, bool) or cardinality < 1:
        raise ContractValidationError(
            schema_ref,
            "CF-REC-005",
            f"vocabulary cardinality must be an integer >= 1, got {cardinality!r}",
        )
    return cardinality


def _from_constructor(schema_ref: str, constructor: Any, *args: Any) -> Any:
    """Invoke the owning contract constructor, translating its validation error."""
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
    """Verify any materialized canonical derived view agrees with authoritative content.

    A producer/storage implementation may materialize a canonical derived value
    for efficiency (Phase 1 § 19). When present, the materialized value must
    equal the value canonically derived from the authoritative content. When
    absent, generic consumers obtain it through contract utilities — a consumer
    never requires redundant materialization.
    """
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
