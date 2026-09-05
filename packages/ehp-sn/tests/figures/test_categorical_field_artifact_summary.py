"""Categorical-field artifact-summary scientific semantics (Phase-4 § 15-17, § 26).

These test the categorical-field-specific semantics of
``figure:categorical-field-artifact-summary/v1`` — the scientific constraints
that do not apply to the graph or raster summaries:

* P4-CAT-002 — no topology dependency: the field summary neither requires nor
  accepts raster-topology/passability semantics as part of its scientific
  meaning (Phase-4 § 15).
* P4-CAT-003 — vocabulary-safe aggregation: category-frequency is partitioned
  by vocabulary identity; no global "category n" frequency is computed across
  vocabularies that share a local integer range (Phase-4 § 17, § 26).
* P4-CAT-SCHEMA — the initial realizability condition constrains
  ``domain.schema == rectangular-row-column/v1``; any other ambient-domain
  schema is a controlled deterministic incompatibility (Phase-4 § 13-14).

Headless Matplotlib backend is selected before any pyplot use.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless backend required

import pytest
from ehp_sn.figures import (
    FigureInputCompatibilityError,
    effective_figure_registry,
    prepare_figure,
)
from ehp_sn.figures.builtin.categorical_field_artifact_summary import (
    _reconstruct_field,
)

from .artifact_summary_helpers import (
    FIELD_ARTIFACT_SUMMARY_REF,
    field_records,
    field_source,
)


def _registry():
    return effective_figure_registry()


def test_category_frequencies_partition_by_vocabulary_identity():
    """Category-frequency partitions never aggregate across vocabulary identities.

    Two records with equal local integer IDs but different vocabulary identities
    must be placed in different partitions; no global 'category n' frequency is
    computed across vocabularies (Phase-4 § 17, § 26 · P4-CAT-003)."""
    projection = prepare_figure(_registry(), FIELD_ARTIFACT_SUMMARY_REF, field_source(field_records()))
    data = projection.content
    partitions = data.vocabulary_partitioned_frequencies
    identities = [p.vocabulary_identity for p in partitions]
    assert "vocab-a" in identities
    assert "vocab-b" in identities
    vocab_a = next(p for p in partitions if p.vocabulary_identity == "vocab-a")
    vocab_b = next(p for p in partitions if p.vocabulary_identity == "vocab-b")
    # Frequencies stay within each vocabulary's own local integer domain.
    assert all(c < 3 for c, _ in vocab_a.frequencies)  # within vocab-a cardinality 3
    assert all(c < 2 for c, _ in vocab_b.frequencies)  # within vocab-b cardinality 2


def test_prepared_view_has_no_topology_dependency():
    """The field summary's prepared view carries no raster-topology semantics.

    A position later blocked by an independently selected topology remains valid
    categorical-field content (Phase-4 § 15 · P4-CAT-002)."""
    projection = prepare_figure(_registry(), FIELD_ARTIFACT_SUMMARY_REF, field_source(field_records()))
    data = projection.content
    assert not hasattr(data, "passable")
    assert not hasattr(data, "component_count")
    assert not hasattr(data, "connected")


def test_unsupported_domain_schema_is_deterministic_incompatibility():
    """A non-rectangular ambient-domain schema is a controlled incompatibility.

    The figure explicitly constrains the ambient-domain schema it knows how to
    spatially realize; it must not assume all future ambient domains are
    rectangular (Phase-4 § 13-14)."""
    content = {
        "domain": {"schema": "some-other/v1", "height": 1, "width": 1, "position_count": 1},
        "vocabulary": {"kind": "anonymous", "identity": "v", "cardinality": 2},
        "observation_id": [0],
    }
    with pytest.raises(FigureInputCompatibilityError):
        _reconstruct_field(content)
