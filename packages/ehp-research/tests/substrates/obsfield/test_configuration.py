"""Behavioral tests for ObsField producer-owned configuration resolution.

Verifies :func:`ehp_research.substrates.obsfield.resolve_configuration`, which
turns a generic parsed document into an immutable, fully effective
:class:`ObsFieldConfiguration`, including an integration check against the
reusable repository profiles under ``config/data/obsfield/``.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest
from ehp_research.substrates.obsfield import (
    ObsFieldConfiguration,
    ObsFieldConfigurationError,
    resolve_configuration,
)
from ehp_sn.configuration import LoadedConfiguration

#: Repo root (…/packages/ehp-research/tests/substrates/obsfield/ → repo).
_REPO_ROOT = Path(__file__).resolve().parents[5]
_OBSFIELD_PROFILES = _REPO_ROOT / "config" / "data" / "obsfield"


def _document(values: Mapping[str, Any], *, source: str = "synthetic.toml") -> LoadedConfiguration:
    return LoadedConfiguration(source=Path(source), values=values)


def _obsfield_document(*, distribution: object = "uniform", cardinality: int = 4) -> LoadedConfiguration:
    return _document(
        {
            "substrate": {"variant": "categorical-complete"},
            "domain": {"schema": "rectangular-row-column/v1", "height": 30, "width": 30},
            "vocabulary": {"identity": "obs-vocabulary:anon/v1", "cardinality": cardinality},
            "assignment": {
                "protocol": "categorical-random/v1",
                "parameters": {"distribution": distribution},
            },
            "generation": {"seed": 0, "realization_count": 100},
        }
    )


def test_minimum_valid_profile_resolves() -> None:
    config = resolve_configuration(_obsfield_document())
    assert isinstance(config, ObsFieldConfiguration)
    assert config.variant == "categorical-complete"
    assert config.assignment_protocol == "categorical-random/v1"
    assert config.distribution == "uniform"
    assert config.realization_count == 100


def test_records_are_frozen() -> None:
    from dataclasses import FrozenInstanceError

    config = resolve_configuration(_obsfield_document())
    with pytest.raises(FrozenInstanceError):
        config.height = 999  # type: ignore[misc]


def test_explicit_probability_vector_resolves() -> None:
    config = resolve_configuration(_obsfield_document(distribution=[0.5, 0.25, 0.15, 0.10]))
    assert config.distribution == (0.5, 0.25, 0.15, 0.10)


def test_probability_vector_length_mismatch_rejected() -> None:
    with pytest.raises(ObsFieldConfigurationError):
        resolve_configuration(_obsfield_document(distribution=[0.5, 0.5, 0.0]))


def test_probability_vector_not_summing_one_rejected() -> None:
    with pytest.raises(ObsFieldConfigurationError):
        resolve_configuration(_obsfield_document(distribution=[0.5, 0.2, 0.1, 0.1]))


def test_invalid_variant_rejected() -> None:
    doc = _obsfield_document()
    doc.values["substrate"]["variant"] = "wrong"  # type: ignore[index]
    with pytest.raises(ObsFieldConfigurationError):
        resolve_configuration(doc)


def test_invalid_domain_schema_rejected() -> None:
    doc = _obsfield_document()
    doc.values["domain"]["schema"] = "hex/v1"  # type: ignore[index]
    with pytest.raises(ObsFieldConfigurationError):
        resolve_configuration(doc)


def test_invalid_domain_dimensions_rejected() -> None:
    doc = _obsfield_document()
    doc.values["domain"]["height"] = 0  # type: ignore[index]
    with pytest.raises(ObsFieldConfigurationError):
        resolve_configuration(doc)


def test_invalid_cardinality_rejected() -> None:
    with pytest.raises(ObsFieldConfigurationError):
        resolve_configuration(_obsfield_document(cardinality=0))


def test_invalid_protocol_rejected() -> None:
    doc = _obsfield_document()
    doc.values["assignment"]["protocol"] = "balanced/v1"  # type: ignore[index]
    with pytest.raises(ObsFieldConfigurationError):
        resolve_configuration(doc)


def test_zero_realization_count_rejected() -> None:
    doc = _obsfield_document()
    doc.values["generation"]["realization_count"] = 0  # type: ignore[index]
    with pytest.raises(ObsFieldConfigurationError):
        resolve_configuration(doc)


def test_repository_profiles_exist() -> None:
    """Both real repository profiles are present for later end-to-end builds."""
    uniform = _OBSFIELD_PROFILES / "uniform-random.toml"
    weighted = _OBSFIELD_PROFILES / "weighted-random.toml"
    assert uniform.exists()
    assert weighted.exists()
