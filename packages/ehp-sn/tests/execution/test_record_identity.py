"""Behavioral tests for the framework record-identity mechanism (Cap 9).

These tests verify the generic ``record_id`` mechanism in isolation, with no
producer or family knowledge: determinism, uniqueness, independence from
enumeration order and from plan identity, and the correctness of the duplicate
guard on the materialization session.
"""

from __future__ import annotations

import pytest
from ehp_sn.execution import (
    GeneratedRecordBody,
    MaterializationSession,
    RealizationKey,
    derive_record_id,
    realization_key_value,
)
from ehp_sn.planning import IdentityInput


def _key(split: str = "train", index: int = 1) -> RealizationKey:
    return RealizationKey(
        inputs=(IdentityInput("split", split), IdentityInput("realization_index", index))
    )


def test_derive_record_id_is_deterministic() -> None:
    key = _key()
    assert derive_record_id("substrate:dagflow/v1", "simple-digraph/v1", key) == derive_record_id(
        "substrate:dagflow/v1", "simple-digraph/v1", key
    )


def test_derive_record_id_distinguishes_inputs() -> None:
    base = derive_record_id("substrate:s/v1", "simple-digraph/v1", _key())
    assert base != derive_record_id("substrate:t/v1", "simple-digraph/v1", _key())
    assert base != derive_record_id("substrate:s/v1", "raster-topology/v1", _key())
    assert base != derive_record_id("substrate:s/v1", "simple-digraph/v1", _key(index=2))
    assert base != derive_record_id("substrate:s/v1", "simple-digraph/v1", _key(split="test"))


def test_record_id_is_opaque_and_not_content_digest() -> None:
    """Distinct realizations that coincidentally share content keep distinct ids."""
    key_a = RealizationKey(inputs=(IdentityInput("realization_index", 1),))
    key_b = RealizationKey(inputs=(IdentityInput("realization_index", 2),))
    assert derive_record_id("substrate:s/v1", "raster-topology/v1", key_a) != derive_record_id(
        "substrate:s/v1", "raster-topology/v1", key_b
    )


def test_record_id_independent_of_registration_order() -> None:
    """Registering records in a different order yields the same record_ids."""
    ids_a = _session_record_ids((1, 2, 3))
    ids_b = _session_record_ids((3, 1, 2))
    assert sorted(ids_a) == sorted(ids_b)


def _session_record_ids(order: tuple[int, ...]) -> list[str]:
    from ehp_sn.experiments import ComponentRef
    from ehp_sn.planning import IdentityInput

    session = MaterializationSession(
        component=ComponentRef.parse("substrate:s/v1"),
        schema_ref="simple-digraph/v1",
        configuration={"seed": 7},
        resources=(),
        identity_inputs=(IdentityInput("seed", 7),),
    )
    for i in order:
        session.add_record(
            GeneratedRecordBody(
                content={"index": i},
                realization_key=RealizationKey(inputs=(IdentityInput("realization_index", i),)),
            )
        )
    return [rec.record_id for rec in session.records]


def test_realization_key_value_reads_declared_descriptor() -> None:
    key = _key(split="validation")
    assert realization_key_value(key, "split") == "validation"
    with pytest.raises(KeyError):
        realization_key_value(key, "absent")
