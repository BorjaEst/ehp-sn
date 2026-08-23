"""Behavioral tests for the generic framework configuration loader (Phase 3B,
Capability 4).

These tests exercise :func:`ehp_sn.configuration.load_configuration` and the
:class:`LoadedConfiguration` document against **synthetic configuration
fixtures** with arbitrary, non-scientific keys. The fixtures never teach the
loader what a substrate, Dagflow, or Maze-ND configuration looks like; they
only prove that the loader reads a source into a generic configuration document
and preserves the parsed structure and source location.

The test matrix required by Capability 4:

* read a valid configuration → parsed values preserved;
* read a nested configuration → nested structure preserved;
* missing path → :class:`ConfigurationAccessError`;
* unreadable / non-file source → controlled generic access failure;
* syntactically invalid TOML → :class:`ConfigurationParseError`;
* the source location accompanies the loaded document.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from ehp_sn.configuration import (
    ConfigurationAccessError,
    ConfigurationParseError,
    LoadedConfiguration,
    load_configuration,
)

_FIXTURES = Path(__file__).resolve().parent / "fixtures"


# ---------------------------------------------------------------------------
# Successful loading
# ---------------------------------------------------------------------------


def test_load_valid_configuration_preserves_parsed_values() -> None:
    """Loading a valid configuration yields the parsed values unchanged."""
    doc = load_configuration(_FIXTURES / "valid.toml")

    assert doc.values == {
        "alpha": {"count": 12, "enabled": True},
        "beta": {"names": ["x", "y"]},
    }


def test_load_valid_configuration_records_source_location() -> None:
    """The loaded document records the source path it was read from."""
    source = _FIXTURES / "valid.toml"
    doc = load_configuration(source)

    assert isinstance(doc, LoadedConfiguration)
    assert doc.source == source.resolve()
    assert doc.source.is_absolute()


def test_load_nested_configuration_preserves_nested_structure() -> None:
    """Nested tables survive loading with their full structure."""
    doc = load_configuration(_FIXTURES / "nested.toml")

    assert doc.values == {
        "alpha": {"count": 12, "enabled": True},
        "beta": {
            "names": ["x", "y"],
            "nested": {
                "depth": 3,
                "flags": [True, False, True],
                "deeper": {"label": "leaf", "value": 1.5},
            },
        },
    }


def test_load_arbitrary_keys_preserves_generic_structure() -> None:
    """Arbitrary non-scientific keys are preserved, not dropped or normalized."""
    doc = load_configuration(_FIXTURES / "arbitrary.toml")

    assert doc.values == {
        "top_level": 42,
        "anything": {"x": 1},
        "elsewhere": {"values": ["a", "b", "c"]},
    }


def test_load_configuration_accepts_str_source() -> None:
    """The loader accepts a plain ``str`` source path."""
    doc = load_configuration(str(_FIXTURES / "valid.toml"))

    assert doc.values["alpha"] == {"count": 12, "enabled": True}


# ---------------------------------------------------------------------------
# Access failures
# ---------------------------------------------------------------------------


def test_load_missing_path_raises_configuration_access_error() -> None:
    """A missing configuration source is an access failure, not a parse one."""
    missing = _FIXTURES / "does-not-exist.toml"

    with pytest.raises(ConfigurationAccessError):
        load_configuration(missing)


def test_load_directory_source_raises_configuration_access_error() -> None:
    """A directory (non-file source) is an access failure."""
    with pytest.raises(ConfigurationAccessError):
        load_configuration(_FIXTURES)


def test_access_error_is_a_configuration_error() -> None:
    """Access failures are part of the generic configuration taxonomy."""
    with pytest.raises(ConfigurationAccessError):
        load_configuration(_FIXTURES / "does-not-exist.toml")


# ---------------------------------------------------------------------------
# Parse failures
# ---------------------------------------------------------------------------


def test_load_invalid_toml_raises_configuration_parse_error() -> None:
    """Syntactically invalid TOML content is a parse error, not an access one."""
    with pytest.raises(ConfigurationParseError):
        load_configuration(_FIXTURES / "invalid.toml")


def test_parse_error_is_a_configuration_error() -> None:
    """Parse failures are part of the generic configuration taxonomy."""
    with pytest.raises(ConfigurationParseError):
        load_configuration(_FIXTURES / "invalid.toml")
