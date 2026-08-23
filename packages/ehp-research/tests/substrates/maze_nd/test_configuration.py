"""Behavioral and cross-profile tests for Capability 5 — Maze-ND producer-owned
configuration resolution.

These tests exercise :func:`ehp_research.substrates.maze_nd.resolve_configuration`,
which turns a generic parsed configuration document (Capability 4's
:class:`ehp_sn.configuration.LoadedConfiguration`) into an immutable,
fully effective :class:`MazeNDConfiguration`.

Unit tests pass **synthetic parsed documents** directly (constructed
:class:`LoadedConfiguration` values) so that precise semantic edge cases are
tested without reading workspace files, touching source files, downloading a
source, or executing any producer.

One integration-style test per family resolves the **actual reusable
repository profile** under ``config/data/maze-nd/``, proving that repository
profiles and the producer schema have not drifted apart.

The matrix required by Capability 5:

* minimum valid explicit profile → resolves;
* fully specified profile → resolves;
* invalid value → producer configuration error;
* invalid combination → producer configuration error;
* missing required scientific choice → producer configuration error.

Deliberately not tested here: source existence/downloading, resource binding,
identity, planning, extraction, deduplication, or generation. Maze-ND config
resolution must not turn into a source-import test.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any

import pytest
from ehp_research.substrates.maze_nd import (
    MazeNDConfiguration,
    MazeNDConfigurationError,
    resolve_configuration,
)
from ehp_sn.configuration import LoadedConfiguration

#: Repo root, located relative to this test file (…/packages/ehp-research/).
_REPO_ROOT = Path(__file__).resolve().parents[5]
_MAZE_ND_PROFILES = _REPO_ROOT / "config" / "data" / "maze-nd"


def _document(values: Mapping[str, Any], *, source: str = "synthetic.toml") -> LoadedConfiguration:
    """Build a generic loaded configuration document from synthetic parsed tables."""
    return LoadedConfiguration(source=Path(source), values=values)


def _maze_document(
    *,
    variant: str = "source-topology",
    reference: str = "UNRESOLVED-EXTERNAL-SOURCE",
    revision: str = "UNRESOLVED-EXTERNAL-SOURCE",
    fingerprint: str = "UNRESOLVED-EXTERNAL-SOURCE",
    schema: str = "maze-nd:extraction/raster/v1",
    selection_policy: str = "complete-source",
    selection_before_dedup: bool = False,
    normalization_policy: str = "maze-nd:normalization/raster/v1",
    connectivity_policy: str = "preserve",
    deduplication_policy: str = "maze-nd:dedup/orientation-preserving-raster/v1",
) -> LoadedConfiguration:
    """A syntactically complete, valid Maze-ND configuration document."""
    return _document(
        {
            "substrate": {"variant": variant},
            "source": {
                "reference": reference,
                "revision": revision,
                "fingerprint": fingerprint,
                "schema": schema,
                "selection_policy": selection_policy,
                "selection_before_dedup": selection_before_dedup,
            },
            "normalization": {"policy": normalization_policy},
            "topology": {
                "connectivity_policy": connectivity_policy,
                "deduplication_policy": deduplication_policy,
            },
        }
    )


# ---------------------------------------------------------------------------
# Successful resolution
# ---------------------------------------------------------------------------


def test_minimum_valid_explicit_profile_resolves() -> None:
    effective = resolve_configuration(_maze_document())

    assert isinstance(effective, MazeNDConfiguration)
    assert effective.variant == "source-topology"
    assert effective.source_reference == "UNRESOLVED-EXTERNAL-SOURCE"
    assert effective.source_revision == "UNRESOLVED-EXTERNAL-SOURCE"
    assert effective.source_fingerprint == "UNRESOLVED-EXTERNAL-SOURCE"
    assert effective.source_schema == "maze-nd:extraction/raster/v1"
    assert effective.source_selection_policy == "complete-source"
    assert effective.selection_before_dedup is False
    assert effective.normalization_policy == "maze-nd:normalization/raster/v1"
    assert effective.connectivity_policy == "preserve"
    assert effective.deduplication_policy == "maze-nd:dedup/orientation-preserving-raster/v1"


def test_fully_specified_profile_resolves() -> None:
    effective = resolve_configuration(
        _maze_document(
            reference="maze-nd-sources",
            revision="rev-2024",
            fingerprint="sha256:abc123",
            schema="maze-nd:extraction/raster/v2",
            selection_policy="select-unique-first",
            selection_before_dedup=True,
            connectivity_policy="reject",
            deduplication_policy="maze-nd:dedup/exact-oriented/v2",
        )
    )

    assert effective.source_reference == "maze-nd-sources"
    assert effective.source_revision == "rev-2024"
    assert effective.source_fingerprint == "sha256:abc123"
    assert effective.source_schema == "maze-nd:extraction/raster/v2"
    assert effective.source_selection_policy == "select-unique-first"
    assert effective.selection_before_dedup is True
    assert effective.connectivity_policy == "reject"
    assert effective.deduplication_policy == "maze-nd:dedup/exact-oriented/v2"


@pytest.mark.parametrize("policy", ["preserve", "reject"])
def test_both_connectivity_policies_resolve(policy: str) -> None:
    effective = resolve_configuration(_maze_document(connectivity_policy=policy))
    assert effective.connectivity_policy == policy


def test_both_selection_orders_resolve() -> None:
    assert (
        resolve_configuration(_maze_document(selection_before_dedup=True)).selection_before_dedup is True
    )
    assert (
        resolve_configuration(_maze_document(selection_before_dedup=False)).selection_before_dedup
        is False
    )


def test_result_is_immutable_frozen_dataclass() -> None:
    effective = resolve_configuration(_maze_document())

    assert isinstance(effective, MazeNDConfiguration)
    # A ``@dataclass(frozen=True)`` raises FrozenInstanceError on attribute
    # reassignment, proving the resolved configuration is immutable.
    with pytest.raises(FrozenInstanceError):
        effective.connectivity_policy = "reject"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# The source is a carried requirement, not a fetched resource
# ---------------------------------------------------------------------------


def test_source_values_are_carried_without_accessing_them() -> None:
    # Resolution must succeed even though the declared source is an unresolved
    # placeholder: Capability 5 carries the requirement and does not attempt to
    # find, download, or bind the source (that is Capability 6 resource binding).
    effective = resolve_configuration(_maze_document())

    assert effective.source_reference == "UNRESOLVED-EXTERNAL-SOURCE"
    assert effective.source_revision == "UNRESOLVED-EXTERNAL-SOURCE"
    assert effective.source_fingerprint == "UNRESOLVED-EXTERNAL-SOURCE"


# ---------------------------------------------------------------------------
# Invalid values → producer configuration error
# ---------------------------------------------------------------------------


def test_invalid_variant_is_rejected() -> None:
    with pytest.raises(MazeNDConfigurationError):
        resolve_configuration(_maze_document(variant="tile-topology"))


def test_invalid_connectivity_policy_is_rejected() -> None:
    with pytest.raises(MazeNDConfigurationError):
        resolve_configuration(_maze_document(connectivity_policy="trim-largest-component"))


def test_non_boolean_selection_before_dedup_is_rejected() -> None:
    doc = _maze_document()
    values = dict(doc.values)
    source = dict(values["source"])  # type: ignore[arg-type]
    source["selection_before_dedup"] = "yes"  # type: ignore[assignment]
    values["source"] = source
    with pytest.raises(MazeNDConfigurationError):
        resolve_configuration(LoadedConfiguration(source=doc.source, values=values))


# ---------------------------------------------------------------------------
# Invalid combinations / unknown keys → producer configuration error
# ---------------------------------------------------------------------------


def test_unknown_producer_key_in_topology_is_rejected() -> None:
    # Reproducible profiles must not silently accept a typo'd key.
    doc = _maze_document()
    values = dict(doc.values)
    topology = dict(values["topology"])  # type: ignore[arg-type]
    topology["connectivty_policy"] = "preserve"  # type: ignore[assignment]
    values["topology"] = topology
    with pytest.raises(MazeNDConfigurationError):
        resolve_configuration(LoadedConfiguration(source=doc.source, values=values))


def test_unknown_producer_key_in_substrate_is_rejected() -> None:
    doc = _document(
        {
            "substrate": {"variant": "source-topology", "foo": 1},
            "source": {
                "reference": "r",
                "revision": "v",
                "fingerprint": "f",
                "schema": "s",
                "selection_policy": "sel",
                "selection_before_dedup": False,
            },
            "normalization": {"policy": "x"},
            "topology": {"connectivity_policy": "preserve", "deduplication_policy": "y"},
        }
    )
    with pytest.raises(MazeNDConfigurationError):
        resolve_configuration(doc)


# ---------------------------------------------------------------------------
# Missing required scientific choice → producer configuration error
# ---------------------------------------------------------------------------


def test_missing_source_reference_is_rejected() -> None:
    with pytest.raises(MazeNDConfigurationError):
        resolve_configuration(_doc_without(_maze_document(), "source.reference"))


def test_missing_source_revision_is_rejected() -> None:
    with pytest.raises(MazeNDConfigurationError):
        resolve_configuration(_doc_without(_maze_document(), "source.revision"))


def test_missing_source_fingerprint_is_rejected() -> None:
    with pytest.raises(MazeNDConfigurationError):
        resolve_configuration(_doc_without(_maze_document(), "source.fingerprint"))


def test_missing_source_schema_is_rejected() -> None:
    with pytest.raises(MazeNDConfigurationError):
        resolve_configuration(_doc_without(_maze_document(), "source.schema"))


def test_missing_selection_policy_is_rejected() -> None:
    with pytest.raises(MazeNDConfigurationError):
        resolve_configuration(_doc_without(_maze_document(), "source.selection_policy"))


def test_missing_selection_before_dedup_is_rejected() -> None:
    with pytest.raises(MazeNDConfigurationError):
        resolve_configuration(_doc_without(_maze_document(), "source.selection_before_dedup"))


def test_missing_normalization_policy_is_rejected() -> None:
    with pytest.raises(MazeNDConfigurationError):
        resolve_configuration(_doc_without(_maze_document(), "normalization.policy"))


def test_missing_connectivity_policy_is_rejected() -> None:
    with pytest.raises(MazeNDConfigurationError):
        resolve_configuration(_doc_without(_maze_document(), "topology.connectivity_policy"))


def test_missing_deduplication_policy_is_rejected() -> None:
    with pytest.raises(MazeNDConfigurationError):
        resolve_configuration(_doc_without(_maze_document(), "topology.deduplication_policy"))


def test_missing_topology_table_is_rejected() -> None:
    with pytest.raises(MazeNDConfigurationError):
        resolve_configuration(_doc_without(_maze_document(), "topology"))


# ---------------------------------------------------------------------------
# Cross-package / profile test (real repository profiles)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "profile_name",
    ["connected-source.toml", "preserve-disconnected-source.toml"],
)
def test_real_maze_nd_profiles_load_and_resolve(profile_name: str) -> None:
    """The committed repository profiles resolve as valid Maze-ND configurations."""
    from ehp_sn.configuration import load_configuration

    profile = _MAZE_ND_PROFILES / profile_name
    assert profile.is_file(), f"expected profile {profile}"

    effective = resolve_configuration(load_configuration(profile))

    assert effective.variant == "source-topology"
    assert effective.source_reference
    assert effective.source_revision
    assert effective.source_fingerprint
    assert effective.source_schema == "maze-nd:extraction/raster/v1"
    assert effective.source_selection_policy == "complete-source"
    assert effective.selection_before_dedup is False
    assert effective.normalization_policy == "maze-nd:normalization/raster/v1"
    assert effective.connectivity_policy in {"preserve", "reject"}
    assert effective.deduplication_policy == "maze-nd:dedup/orientation-preserving-raster/v1"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _doc_without(doc: LoadedConfiguration, dotted_path: str) -> LoadedConfiguration:
    """Return a copy of ``doc`` with the field at ``dotted_path`` removed."""
    values = dict(doc.values)
    parts = dotted_path.split(".")
    table = values
    for part in parts[:-1]:
        table = table[part]  # type: ignore[index]
    assert parts[-1] in table, f"field {dotted_path} not present in document"
    del table[parts[-1]]  # type: ignore[arg-type]
    return LoadedConfiguration(source=doc.source, values=values)
