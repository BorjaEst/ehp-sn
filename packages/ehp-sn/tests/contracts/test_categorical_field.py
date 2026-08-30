"""Contract tests for the shared ``categorical-field/v1`` record schema.

Verifies the ``ehp_sn``-owned implementation of
``docs/docs/framework/contracts/observations/categorical-field-v1.md``: total
categorical persistent coverage, canonical position ordering, vocabulary bounds,
and the anonymous/external vocabulary contract. The constructor accepts only
contract-owned authoritative inputs (resolved domain, resolved vocabulary, and
observation IDs in canonical position order) and knows nothing about a producing
family, seed, topology, passability, or split.

The shared-validator section covers the framework-owned ``CF-REC-00x``
conformance boundary (``ehp_sn.contracts.validation.validate_categorical_field``):
lossless decode preservation, distinct vocabulary identities, the negative
schema-drift rejection that ``extent`` is not an alias for ``domain``, and the
``CF-REC-006`` topology-leak rejection.
"""

from __future__ import annotations

import pytest
from ehp_sn.contracts.domains import rectangular_row_column_domain
from ehp_sn.contracts.observations import (
    AnonymousVocabulary,
    CategoricalFieldError,
    ExternalVocabulary,
    categorical_field,
)
from ehp_sn.contracts.validation import (
    ContractValidationError,
    validate_categorical_field,
)


def _domain(h: int = 2, w: int = 3):
    return rectangular_row_column_domain(h, w)


def test_same_domain_vocabulary_assignment_same_content() -> None:
    """Same domain + vocabulary + assignments → same canonical field content."""
    domain = _domain()
    vocab = AnonymousVocabulary(identity="vocab:a/v1", cardinality=3)
    a = categorical_field(domain, vocab, [1, 2, 0, 2, 1, 0])
    b = categorical_field(_domain(), vocab, [1, 2, 0, 2, 1, 0])
    assert a.content() == b.content()


def test_canonical_position_order_is_respected() -> None:
    """observation_id is indexed by canonical position_id order (CF-REC-002)."""
    domain = _domain()
    vocab = AnonymousVocabulary(identity="vocab:a/v1", cardinality=2)
    field = categorical_field(domain, vocab, [0, 1, 0, 1, 0, 1])
    assert field.observation_ids == (0, 1, 0, 1, 0, 1)
    assert len(field.observation_ids) == domain.position_count


def test_fixed_schema_semantics() -> None:
    """coverage=total, value_kind=categorical, persistent=true are fixed."""
    field = categorical_field(_domain(), AnonymousVocabulary("v", 2), [0, 1, 0, 1, 0, 1])
    assert field.coverage == "total"
    assert field.value_kind == "categorical"
    assert field.persistent is True


def test_assignment_count_mismatch_rejected() -> None:
    """Length mismatch vs position_count is rejected (CF-REC-002)."""
    with pytest.raises(CategoricalFieldError):
        categorical_field(_domain(), AnonymousVocabulary("v", 3), [1, 2, 0])


def test_out_of_range_observation_id_rejected() -> None:
    """Values outside the vocabulary domain are rejected (CF-REC-004)."""
    with pytest.raises(CategoricalFieldError):
        categorical_field(_domain(), AnonymousVocabulary("v", 3), [1, 2, 0, 2, 1, 3])


def test_vocabulary_identity_not_cardinality_alone() -> None:
    """Two vocabularies of equal cardinality but different identity differ."""
    a = categorical_field(_domain(), AnonymousVocabulary("identity-a", 3), [1, 2, 0, 2, 1, 0])
    b = categorical_field(_domain(), AnonymousVocabulary("identity-b", 3), [1, 2, 0, 2, 1, 0])
    assert a.content() != b.content()


def test_external_vocabulary_form() -> None:
    """The external vocabulary form is representable with immutable identity."""
    vocab = ExternalVocabulary(ref="vocab:external-x/v1", identity="resolved-immutable", cardinality=2)
    field = categorical_field(_domain(), vocab, [0, 1, 0, 1, 0, 1])
    assert field.vocabulary.kind == "external"
    assert field.vocabulary.declaration()["ref"] == "vocab:external-x/v1"


def test_no_topology_requires_passability_or_split() -> None:
    """A field is self-contained and topology-independent (CF-REC-006)."""
    field = categorical_field(_domain(), AnonymousVocabulary("v", 2), [0, 1, 0, 1, 0, 1])
    # The constructor never accepts topology/passability/split inputs.
    content = field.content()
    assert "topology" not in content
    assert "passable" not in content
    assert "split" not in content


# ---------------------------------------------------------------------------
# Shared validator (CF-REC conformance boundary)
#
# The validator operates on the declared logical instance (decoded dict) and is
# the boundary that keeps normal loading non-repairing (Phase 1 § 8–9, § 34).
# ---------------------------------------------------------------------------


def _field_instance() -> dict:
    """A valid ``categorical-field/v1`` declared logical instance (CF-33 fixture)."""
    return {
        "domain": {"height": 2, "width": 3, "schema": "rectangular-row-column/v1"},
        "vocabulary": {"kind": "anonymous", "identity": "vocab-alpha", "cardinality": 3},
        "observation_id": [2, 0, 1, 1, 2, 0],
    }


def test_validate_preserves_observations_exactly() -> None:
    """The validator preserves domain, vocabulary identity, and observation_id."""
    field = validate_categorical_field(_field_instance())
    assert field.domain.height == 2
    assert field.domain.width == 3
    assert tuple(field.observation_ids) == (2, 0, 1, 1, 2, 0)
    assert field.vocabulary.identity == "vocab-alpha"
    assert field.vocabulary.cardinality == 3


def test_validate_distinct_vocabulary_identities_remain_distinct() -> None:
    """Two vocabularies of equal cardinality but different identity differ (CF-33)."""
    a = validate_categorical_field(
        {
            **_field_instance(),
            "vocabulary": {"kind": "anonymous", "identity": "vocab-A", "cardinality": 3},
        }
    )
    b = validate_categorical_field(
        {
            **_field_instance(),
            "vocabulary": {"kind": "anonymous", "identity": "vocab-B", "cardinality": 3},
        }
    )
    assert a.vocabulary.identity != b.vocabulary.identity
    assert a.vocabulary.cardinality == b.vocabulary.cardinality == 3
    assert a.content() != b.content()


def test_validate_rejects_extent_as_domain_alias() -> None:
    """A ``categorical-field/v1`` instance carrying ``extent`` is rejected (CF-REC-001)."""
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


def test_validate_rejects_topology_leak() -> None:
    """A field with a topology parent reference fails CF-REC-006."""
    with pytest.raises(ContractValidationError) as exc:
        validate_categorical_field({**_field_instance(), "topology_record_id": "sha256:TOPO"})
    assert exc.value.invariant == "CF-REC-006"
