"""Phase 1 shared-contract validation and negative schema-drift tests.

This test module verifies the framework-owned shared validators in
:mod:`ehp_sn.contracts.validation` — the one authority for validating each
shared logical schema and the boundary that makes normal loading
non-repairing (Phase 1 § 8–9, § 19, § 34; ``docs/invariants.md`` ARCH-014).

It covers:

* lossless-decode conformance fixtures that decode into exact logical values
  before validation (Phase 1 § 29–33);
* shared-contract validation of ``simple-digraph/v1``, ``raster-topology/v1``,
  and ``categorical-field/v1`` declared logical instances (Phase 1 § 21–24);
* materialized derived-view agreement (Phase 1 § 19);
* the negative schema-drift cases of Phase 1 § 34 — a loader may decode a
  malformed record but must never silently transform it into a conforming one;
* categorical topology leak rejection (``CF-REC-006``, Phase 1 § 34).

The authoritative-and-derived separation (Phase 1 § 18) is asserted by
validation success on authoritative content only and by derived-view agreement
checks.
"""

from __future__ import annotations

import pytest
from ehp_sn.contracts.validation import (
    ContractValidationError,
    validate_categorical_field,
    validate_raster_topology,
    validate_simple_digraph,
)

# ---------------------------------------------------------------------------
# lossless-decode conformance fixtures (Phase 1 § 30-33)
# ---------------------------------------------------------------------------


def _digraph_fixture() -> dict:
    """A valid ``simple-digraph/v1`` declared logical instance (SG-31 fixture)."""
    return {
        "node_count": 4,
        "edges": [[0, 1], [0, 2], [1, 3], [2, 3]],
    }


def _raster_fixture(domain: dict | None = None, passable: list | None = None) -> dict:
    """A valid ``raster-topology/v1`` declared logical instance (RT-32 fixture)."""
    domain = domain or {"height": 2, "width": 3, "schema": "rectangular-row-column/v1"}
    passable = passable or [True, True, False, False, True, True]
    return {"extent": domain, "passable": passable}


def _field_fixture() -> dict:
    """A valid ``categorical-field/v1`` declared logical instance (CF-33 fixture)."""
    return {
        "domain": {"height": 2, "width": 3, "schema": "rectangular-row-column/v1"},
        "vocabulary": {"kind": "anonymous", "identity": "vocab-alpha", "cardinality": 3},
        "observation_id": [2, 0, 1, 1, 2, 0],
    }


# ---------------------------------------------------------------------------
# decoder conformance — decode asserts exact logical values (Phase 1 § 29-30)
# ---------------------------------------------------------------------------


def test_decode_simple_digraph_preserves_edges_exactly() -> None:
    """Edges and node_count are preserved exactly through validation."""
    graph = validate_simple_digraph(_digraph_fixture())
    assert graph.node_count == 4
    # Canonical lexicographic ordering is preserved; no reordering/repair of the
    # value itself.
    assert list(graph.edges) == [(0, 1), (0, 2), (1, 3), (2, 3)]
    assert graph.content()["edges"] == [(0, 1), (0, 2), (1, 3), (2, 3)]


def test_decode_raster_preserves_passable_exactly() -> None:
    """Passable sequence and ambient-domain declaration are preserved exactly."""
    fixture = _raster_fixture(passable=[True, False, True, False, False, True])
    topology = validate_raster_topology(fixture)
    assert tuple(topology.passable) == (True, False, True, False, False, True)
    assert topology.extent.height == 2
    assert topology.extent.width == 3
    assert topology.extent.position_count == 6
    # position_id(r,c) = r * width + c (Phase 1 § 32).
    assert topology.extent.position_id(1, 2) == 5


def test_decode_categorical_field_preserves_observations_exactly() -> None:
    """domain, vocabulary identity, and observation_id are preserved exactly."""
    field = validate_categorical_field(_field_fixture())
    assert field.domain.height == 2
    assert field.domain.width == 3
    assert tuple(field.observation_ids) == (2, 0, 1, 1, 2, 0)
    assert field.vocabulary.identity == "vocab-alpha"
    assert field.vocabulary.cardinality == 3


def test_distinct_vocabulary_identities_remain_distinct() -> None:
    """Two vocabularies of equal cardinality/range but different identity differ (CF-33)."""
    a = validate_categorical_field(
        {
            **_field_fixture(),
            "vocabulary": {"kind": "anonymous", "identity": "vocab-A", "cardinality": 3},
        }
    )
    b = validate_categorical_field(
        {
            **_field_fixture(),
            "vocabulary": {"kind": "anonymous", "identity": "vocab-B", "cardinality": 3},
        }
    )
    assert a.vocabulary.identity != b.vocabulary.identity
    assert a.vocabulary.cardinality == b.vocabulary.cardinality == 3
    assert a.content()["vocabulary"]["identity"] != b.content()["vocabulary"]["identity"]


# ---------------------------------------------------------------------------
# materialized derived-view agreement (Phase 1 § 19)
# ---------------------------------------------------------------------------


def test_materialized_derived_view_agrees_with_authoritative() -> None:
    """A stored derived value equal to the canonical value is accepted."""
    graph = validate_simple_digraph({**_digraph_fixture(), "acyclic": True, "terminal_count": 1})
    assert graph.acyclic is True


def test_materialized_derived_view_disagreement_is_rejected() -> None:
    """A stored derived value that disagrees with authoritative content fails."""
    with pytest.raises(ContractValidationError) as exc:
        validate_simple_digraph({**_digraph_fixture(), "acyclic": False})
    assert exc.value.invariant == "SG-REC-006"


def test_materialized_raster_derived_view_disagreement_is_rejected() -> None:
    with pytest.raises(ContractValidationError) as exc:
        validate_raster_topology({**_raster_fixture(), "connected": False})
    assert exc.value.invariant == "RT-REC-007"


# ---------------------------------------------------------------------------
# negative schema drift (Phase 1 § 34) — never silently repaired
# ---------------------------------------------------------------------------


def test_raster_domain_is_not_an_extent_alias() -> None:
    """raster-topology/v1 containing `domain` (missing `extent`) fails validation."""
    with pytest.raises(ContractValidationError) as exc:
        validate_raster_topology(
            {
                "domain": {"height": 2, "width": 3, "schema": "rectangular-row-column/v1"},
                "passable": [True] * 6,
            }
        )
    assert exc.value.schema_ref == "raster-topology/v1"
    assert exc.value.invariant == "RT-REC-001"


def test_categorical_extent_is_not_a_domain_alias() -> None:
    """categorical-field/v1 containing `extent` (missing `domain`) fails validation."""
    with pytest.raises(ContractValidationError) as exc:
        validate_categorical_field(
            {
                "extent": {"height": 2, "width": 3, "schema": "rectangular-row-column/v1"},
                "vocabulary": {"kind": "anonymous", "identity": "v", "cardinality": 3},
                "observation_id": [0] * 6,
            }
        )
    assert exc.value.schema_ref == "categorical-field/v1"
    assert exc.value.invariant == "CF-REC-001"


def test_successor_table_is_not_an_edges_alias() -> None:
    """simple-digraph/v1 containing a successor table (missing edges) fails."""
    with pytest.raises(ContractValidationError) as exc:
        validate_simple_digraph({"node_count": 4, "successor": [[1], [2], [3], []]})
    assert exc.value.schema_ref == "simple-digraph/v1"
    assert exc.value.invariant == "SG-REC-001"


def test_categorical_topology_leak_is_rejected() -> None:
    """categorical-field/v1 with a topology parent reference fails CF-REC-006."""
    with pytest.raises(ContractValidationError) as exc:
        validate_categorical_field({**_field_fixture(), "topology_record_id": "sha256:TOPO"})
    assert exc.value.invariant == "CF-REC-006"


# ---------------------------------------------------------------------------
# validator rejects malformed authoritative content (not silently repaired)
# ---------------------------------------------------------------------------


def test_raster_incorrect_passable_length_rejected() -> None:
    """An incorrect passable length remains invalid (RT-REC-002)."""
    with pytest.raises(ContractValidationError):
        validate_raster_topology(_raster_fixture(passable=[True] * 5))


def test_raster_zero_passable_cells_rejected() -> None:
    """A fully blocked passable structure remains invalid (RT-REC-002)."""
    with pytest.raises(ContractValidationError):
        validate_raster_topology(_raster_fixture(passable=[False] * 6))


def test_simple_digraph_invalid_endpoint_rejected() -> None:
    """An edge endpoint outside the node domain remains invalid (SG-REC-002)."""
    with pytest.raises(ContractValidationError):
        validate_simple_digraph({"node_count": 2, "edges": [[0, 5]]})


def test_simple_digraph_duplicate_edge_rejected() -> None:
    """A duplicate edge remains invalid (SG-REC-003)."""
    with pytest.raises(ContractValidationError):
        validate_simple_digraph({"node_count": 3, "edges": [[0, 1], [0, 1]]})


def test_simple_digraph_self_loop_rejected() -> None:
    """A self-loop remains invalid (SG-REC-003)."""
    with pytest.raises(ContractValidationError):
        validate_simple_digraph({"node_count": 3, "edges": [[0, 0]]})


def test_categorical_out_of_bounds_observation_rejected() -> None:
    """An observation ID outside the vocabulary remains invalid (CF-REC-004)."""
    with pytest.raises(ContractValidationError):
        validate_categorical_field({**_field_fixture(), "observation_id": [3, 0, 1, 1, 2, 0]})
