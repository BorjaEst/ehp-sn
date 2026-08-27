"""Contract tests for the shared ``categorical-field/v1`` record schema.

Verifies the ``ehp_sn``-owned implementation of
``docs/docs/framework/contracts/observations/categorical-field-v1.md``: total
categorical persistent coverage, canonical position ordering, vocabulary bounds,
and the anonymous/external vocabulary contract. The constructor accepts only
contract-owned authoritative inputs (resolved domain, resolved vocabulary, and
observation IDs in canonical position order) and knows nothing about a producing
family, seed, topology, passability, or split.
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
