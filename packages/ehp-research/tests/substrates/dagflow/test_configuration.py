"""Behavioral and cross-profile tests for Capability 5 — Dagflow producer-owned
configuration resolution.

These tests exercise :func:`ehp_research.substrates.dagflow.resolve_configuration`,
which turns a generic parsed configuration document (Capability 4's
:class:`ehp_sn.configuration.LoadedConfiguration`) into an immutable,
fully effective :class:`DagflowConfiguration`.

Unit tests pass **synthetic parsed documents** directly (constructed
:class:`LoadedConfiguration` values) so that precise semantic edge cases are
tested without reading workspace files or executing any producer.

One integration-style test per family resolves the **actual reusable
repository profiles** under ``config/data/dagflow/``, proving that repository
profiles and the producer schema have not drifted apart (Capability 4 proves
only syntactic loading; this proves profile-level semantic validity).

The matrix required by Capability 5:

* minimum valid explicit profile → resolves;
* fully specified profile → resolves;
* invalid value → producer configuration error;
* invalid combination → producer configuration error;
* missing required scientific choice → producer configuration error.

This test module deliberately does **not** test graph generation, resource
binding, identity, planning, or source access (those are later capabilities).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any

import pytest
from ehp_research.substrates.dagflow import (
    DagflowConfiguration,
    DagflowConfigurationError,
    resolve_configuration,
)
from ehp_sn.configuration import LoadedConfiguration

#: Repo root, located relative to this test file (…/packages/ehp-research/).
_REPO_ROOT = Path(__file__).resolve().parents[5]
_DAGFLOW_PROFILES = _REPO_ROOT / "config" / "data" / "dagflow"


def _document(values: Mapping[str, Any], *, source: str = "synthetic.toml") -> LoadedConfiguration:
    """Build a generic loaded configuration document from synthetic parsed tables."""
    return LoadedConfiguration(source=Path(source), values=values)


def _dagflow_document(
    *,
    variant: str = "single-terminal",
    protocol: str = "constructive-forward/v1",
    seed: int = 1729,
    node_count: int | None = 16,
    minimum: int | None = None,
    maximum: int | None = None,
    distribution: str | None = None,
    probability: float = 0.10,
    train: int = 10000,
    validation: int = 1000,
    test: int = 1000,
) -> LoadedConfiguration:
    """A syntactically complete, valid Dagflow configuration document."""
    graph: dict[str, object] = {"additional_edge_probability": probability}
    if node_count is not None:
        graph["node_count"] = node_count
    if minimum is not None or maximum is not None or distribution is not None:
        node_count_policy: dict[str, object] = {}
        if minimum is not None:
            node_count_policy["minimum"] = minimum
        if maximum is not None:
            node_count_policy["maximum"] = maximum
        if distribution is not None:
            node_count_policy["distribution"] = distribution
        graph["node_count"] = node_count_policy
    return _document(
        {
            "substrate": {"variant": variant},
            "generation": {"protocol": protocol, "seed": seed},
            "graph": graph,
            "splits": {
                "train": {"count": train},
                "validation": {"count": validation},
                "test": {"count": test},
            },
        }
    )


# ---------------------------------------------------------------------------
# Successful resolution
# ---------------------------------------------------------------------------


def test_minimum_valid_explicit_profile_resolves() -> None:
    effective = resolve_configuration(_dagflow_document())

    assert isinstance(effective, DagflowConfiguration)
    assert effective.variant == "single-terminal"
    assert effective.generation_protocol == "constructive-forward/v1"
    assert effective.seed == 1729
    assert effective.node_count == 16
    assert effective.node_count_minimum is None
    assert effective.node_count_maximum is None
    assert effective.node_count_distribution is None
    assert effective.additional_edge_probability == 0.10
    assert effective.splits_train_count == 10000
    assert effective.splits_validation_count == 1000
    assert effective.splits_test_count == 1000


def test_fully_specified_fixed_profile_resolves() -> None:
    effective = resolve_configuration(
        _dagflow_document(
            variant="single-terminal",
            protocol="layered-terminal/v1",
            seed=7,
            node_count=64,
            probability=0.40,
        )
    )

    assert effective.variant == "single-terminal"
    assert effective.generation_protocol == "layered-terminal/v1"
    assert effective.seed == 7
    assert effective.node_count == 64
    assert effective.additional_edge_probability == 0.40


def test_bounded_node_count_policy_resolves() -> None:
    effective = resolve_configuration(
        _dagflow_document(node_count=None, minimum=8, maximum=64, distribution="uniform")
    )

    assert effective.node_count is None
    assert effective.node_count_minimum == 8
    assert effective.node_count_maximum == 64
    assert effective.node_count_distribution == "uniform"


def test_result_is_immutable_frozen_dataclass() -> None:
    effective = resolve_configuration(_dagflow_document())

    assert isinstance(effective, DagflowConfiguration)
    # A ``@dataclass(frozen=True)`` raises FrozenInstanceError on attribute
    # reassignment, proving the resolved configuration is immutable.
    with pytest.raises(FrozenInstanceError):
        effective.node_count = 999  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Values at the permitted range boundary
# ---------------------------------------------------------------------------


def test_probability_boundaries_are_accepted() -> None:
    assert resolve_configuration(_dagflow_document(probability=0.0)).additional_edge_probability == 0.0
    assert resolve_configuration(_dagflow_document(probability=1.0)).additional_edge_probability == 1.0


def test_zero_split_counts_are_accepted() -> None:
    effective = resolve_configuration(_dagflow_document(train=0, validation=0, test=0))
    assert effective.splits_train_count == 0
    assert effective.splits_validation_count == 0
    assert effective.splits_test_count == 0


def test_single_node_count_is_accepted() -> None:
    effective = resolve_configuration(_dagflow_document(node_count=1))
    assert effective.node_count == 1


# ---------------------------------------------------------------------------
# Invalid values → producer configuration error
# ---------------------------------------------------------------------------


def test_invalid_variant_is_rejected() -> None:
    with pytest.raises(DagflowConfigurationError):
        resolve_configuration(_dagflow_document(variant="multi-terminal"))


def test_zero_node_count_is_rejected() -> None:
    with pytest.raises(DagflowConfigurationError):
        resolve_configuration(_dagflow_document(node_count=0))


def test_negative_node_count_is_rejected() -> None:
    with pytest.raises(DagflowConfigurationError):
        resolve_configuration(_dagflow_document(node_count=-5))


def test_negative_seed_is_rejected() -> None:
    with pytest.raises(DagflowConfigurationError):
        resolve_configuration(_dagflow_document(seed=-1))


def test_probability_out_of_range_is_rejected() -> None:
    with pytest.raises(DagflowConfigurationError):
        resolve_configuration(_dagflow_document(probability=1.5))


def test_negative_probability_is_rejected() -> None:
    with pytest.raises(DagflowConfigurationError):
        resolve_configuration(_dagflow_document(probability=-0.1))


def test_negative_split_count_is_rejected() -> None:
    with pytest.raises(DagflowConfigurationError):
        resolve_configuration(_dagflow_document(train=-1))


# ---------------------------------------------------------------------------
# Invalid combinations → producer configuration error
# ---------------------------------------------------------------------------


def test_incomplete_bounded_policy_is_rejected() -> None:
    # Only minimum present; the bounded triple must be complete.
    with pytest.raises(DagflowConfigurationError):
        resolve_configuration(
            _dagflow_document(
                node_count=None,
                minimum=8,
                maximum=None,
                distribution=None,
            )
        )


def test_bounded_maximum_less_than_minimum_is_rejected() -> None:
    with pytest.raises(DagflowConfigurationError):
        resolve_configuration(
            _dagflow_document(node_count=None, minimum=64, maximum=8, distribution="uniform")
        )


# ---------------------------------------------------------------------------
# Missing required scientific choice → producer configuration error
# ---------------------------------------------------------------------------


def test_missing_variant_is_rejected() -> None:
    doc = _document(
        {
            "generation": {"protocol": "constructive-forward/v1", "seed": 1729},
            "graph": {"node_count": 16, "additional_edge_probability": 0.10},
            "splits": {"train": {"count": 1}, "validation": {"count": 1}, "test": {"count": 1}},
        }
    )
    with pytest.raises(DagflowConfigurationError):
        resolve_configuration(doc)


def test_missing_protocol_is_rejected() -> None:
    doc = _doc_without(_dagflow_document(), "generation.protocol")
    with pytest.raises(DagflowConfigurationError):
        resolve_configuration(doc)


def test_missing_seed_is_rejected() -> None:
    doc = _doc_without(_dagflow_document(), "generation.seed")
    with pytest.raises(DagflowConfigurationError):
        resolve_configuration(doc)


def test_missing_node_count_policy_is_rejected() -> None:
    doc = _doc_without(_dagflow_document(), "graph.node_count")
    with pytest.raises(DagflowConfigurationError):
        resolve_configuration(doc)


def test_missing_additional_edge_probability_is_rejected() -> None:
    doc = _doc_without(_dagflow_document(), "graph.additional_edge_probability")
    with pytest.raises(DagflowConfigurationError):
        resolve_configuration(doc)


def test_missing_split_table_is_rejected() -> None:
    doc = _doc_without(_dagflow_document(), "splits")
    with pytest.raises(DagflowConfigurationError):
        resolve_configuration(doc)


def test_missing_train_split_count_is_rejected() -> None:
    doc = _doc_without(_dagflow_document(), "splits.train.count")
    with pytest.raises(DagflowConfigurationError):
        resolve_configuration(doc)


# ---------------------------------------------------------------------------
# Cross-package / profile test (real repository profiles)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "profile_name",
    ["constructive-dense.toml", "constructive-sparse.toml"],
)
def test_real_dagflow_profiles_load_and_resolve(profile_name: str) -> None:
    """The committed repository profiles resolve as valid Dagflow configurations."""
    from ehp_sn.configuration import load_configuration

    profile = _DAGFLOW_PROFILES / profile_name
    assert profile.is_file(), f"expected profile {profile}"

    effective = resolve_configuration(load_configuration(profile))

    assert effective.variant == "single-terminal"
    assert effective.generation_protocol == "constructive-forward/v1"
    assert effective.seed >= 0
    assert effective.node_count is not None and effective.node_count >= 1
    assert 0.0 <= effective.additional_edge_probability <= 1.0
    assert effective.splits_train_count >= 0
    assert effective.splits_validation_count >= 0
    assert effective.splits_test_count >= 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _doc_without(doc: LoadedConfiguration, dotted_path: str) -> LoadedConfiguration:
    """Return a copy of ``doc`` with the field at ``dotted_path`` removed.

    ``dotted_path`` addresses nested tables, e.g. ``"splits.train.count"``.
    The top-level table remains if it still has other fields; otherwise it is
    removed too so the "missing table" and "missing field" cases are both
    exercised naturally.
    """
    values = dict(doc.values)
    parts = dotted_path.split(".")
    table = values
    for part in parts[:-1]:
        table = table[part]  # type: ignore[index]
    assert parts[-1] in table, f"field {dotted_path} not present in document"
    del table[parts[-1]]  # type: ignore[arg-type]
    return LoadedConfiguration(source=doc.source, values=values)
