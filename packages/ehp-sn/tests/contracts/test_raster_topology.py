"""Contract tests for the shared ``raster-topology/v1`` record schema.

Verifies the ``ehp_sn``-owned implementation of
``docs/docs/framework/contracts/topology/raster-topology-v1.md``: authoritative
passability, fixed derived views (states, movement, connectivity) under the fixed
grid4/undirected/unit/no-stay parameters, and the invariant rejections.

Target 15 acceptance: the same constructor accepts normalized passability from
any producer context (both raster producers hand only extent + passable), and it
owns no producer-specific semantics such as source lineage, generator profile,
connectivity acceptance policy, largest-component selection, or retry.

The shared-validator section covers the framework-owned ``RT-REC-00x``
conformance boundary (``ehp_sn.contracts.validation.validate_raster_topology``):
lossless decode preservation, the negative schema-drift rejection that a
historical ``domain`` field is not an alias for authoritative ``extent``, and
materialized derived-view agreement.
"""

from __future__ import annotations

import pytest
from ehp_sn.contracts.domains import rectangular_row_column_domain
from ehp_sn.contracts.topology import (
    MOVEMENT_KIND,
    RasterTopologyError,
    raster_topology,
)
from ehp_sn.contracts.validation import (
    ContractValidationError,
    validate_raster_topology,
)


def _domain(h: int = 2, w: int = 3):
    return rectangular_row_column_domain(h, w)


def test_state_enumeration_row_major() -> None:
    """Compact states enumerate passable positions in row-major order (RT-REC-003)."""
    topology = raster_topology(_domain(), [True, True, False, False, True, True])
    assert topology.state_count == 4
    assert topology.state_to_position == (0, 1, 4, 5)
    assert topology.position_to_state == (0, 1, None, None, 2, 3)


def test_movement_relation_grid4_undirected_no_stay() -> None:
    """Derived movement matches grid4/undirected/unit/no-stay (RT-REC-004..006)."""
    topology = raster_topology(_domain(2, 3), [True, True, True, True, True, True])
    # state 0 (position 0) neighbors east (1) and south (3)
    assert topology.next_state[0] == {"east": 1, "south": 3}
    assert topology.movement_valid[0]["east"] is True
    assert topology.movement_valid[0]["north"] is False
    assert topology.movement_valid[0]["west"] is False
    # undirected: neighbor 1 has a west transition back to 0
    assert topology.next_state[1]["west"] == 0
    # no stay / no self-loop (RT-REC-006): no state transitions to itself
    assert all(target != state for state in range(6) for target in topology.next_state[state].values())
    assert MOVEMENT_KIND == "grid4"


def test_connected_and_component_count() -> None:
    """connected/component_count agree with grid4 adjacency (RT-REC-007)."""
    connected = raster_topology(_domain(), [True, True, False, False, True, True])
    assert connected.connected is True
    assert connected.component_count == 1

    split = raster_topology(_domain(), [True, False, False, False, False, True])
    assert split.connected is False
    assert split.component_count == 2


def test_passable_length_mismatch_rejected() -> None:
    """passable must have exactly position_count entries (RT-REC-002)."""
    with pytest.raises(RasterTopologyError):
        raster_topology(_domain(), [True, True, True])


def test_all_blocked_rejected() -> None:
    """At least one position must be passable (state_count >= 1, RT-REC-002)."""
    with pytest.raises(RasterTopologyError):
        raster_topology(_domain(), [False] * 6)


def test_authoritative_content_is_extent_plus_passable() -> None:
    """Record identity/equality rests on extent + passable, not derived views."""
    topology = raster_topology(_domain(), [True, True, False, False, True, True])
    content = topology.content()
    assert set(content.keys()) == {"extent", "passable"}
    assert content["passable"] == [True, True, False, False, True, True]


def test_same_constructor_accepts_two_normalized_producer_contexts() -> None:
    """Gate C: exactly the same constructor accepts normalized passability
    from any producer context (e.g. two synthetic producers)."""
    domain = _domain(3, 3)
    producer_a_passable = [True, True, False, True, True, False, True, True, True]
    producer_b_passable = [False, True, True, False, True, True, True, True, True]

    topology_a = raster_topology(domain, producer_a_passable)
    topology_b = raster_topology(domain, producer_b_passable)

    # The constructor accepts either normalized passability and derives views.
    assert topology_a.state_count == producer_a_passable.count(True)
    assert topology_b.state_count == producer_b_passable.count(True)
    assert topology_a.connected != topology_b.connected or topology_a.content() != topology_b.content()


def test_constructor_owns_no_producer_specific_semantics() -> None:
    """The constructor takes only extent + passable; nothing product-specific."""
    import inspect

    signature = inspect.signature(raster_topology)
    params = list(signature.parameters)
    assert params == ["extent", "passable"]


# ---------------------------------------------------------------------------
# Shared validator (RT-REC conformance boundary)
#
# The validator operates on the declared logical instance (decoded dict) and is
# the boundary that keeps normal loading non-repairing (Phase 1 § 8–9, § 34).
# ---------------------------------------------------------------------------


def _raster_instance(*, extent: dict | None = None, passable: list | None = None) -> dict:
    """A valid ``raster-topology/v1`` declared logical instance (RT-32 fixture)."""
    extent = extent or {"height": 2, "width": 3, "schema": "rectangular-row-column/v1"}
    passable = passable or [True, True, False, False, True, True]
    return {"extent": extent, "passable": passable}


def test_validate_preserves_passable_exactly() -> None:
    """The validator preserves passable and the extent declaration exactly."""
    fixture = _raster_instance(passable=[True, False, True, False, False, True])
    topology = validate_raster_topology(fixture)
    assert tuple(topology.passable) == (True, False, True, False, False, True)
    assert topology.extent.height == 2
    assert topology.extent.width == 3
    assert topology.extent.position_count == 6
    # position_id(r,c) = r * width + c (Phase 1 § 32).
    assert topology.extent.position_id(1, 2) == 5


def test_validate_rejects_domain_as_extent_alias() -> None:
    """A ``raster-topology/v1`` instance carrying ``domain`` is rejected (RT-REC-001).

    The historical raster ``domain`` field is not an alias for the authoritative
    ``extent``; such an instance is invalid current-schema content and must not
    be silently repaired.
    """
    with pytest.raises(ContractValidationError) as exc:
        validate_raster_topology(
            {
                "domain": {"height": 2, "width": 3, "schema": "rectangular-row-column/v1"},
                "passable": [True] * 6,
            }
        )
    assert exc.value.schema_ref == "raster-topology/v1"
    assert exc.value.invariant == "RT-REC-001"


def test_validate_materialized_derived_view_disagreement_rejected() -> None:
    """A stored derived value disagreeing with authoritative content fails (RT-REC-007)."""
    with pytest.raises(ContractValidationError) as exc:
        validate_raster_topology({**_raster_instance(), "connected": False})
    assert exc.value.invariant == "RT-REC-007"
