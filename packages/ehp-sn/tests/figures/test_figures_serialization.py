"""Serialization-policy tests for :mod:`ehp_sn.figures.serialization`.

These validate the Phase-4 serialization-policy contract
(``docs/docs/framework/figures/rendering.md`` § "Serialization request"; Phase-4
· P4-T3):

* the policy is explicit and fully resolved before serialization;
* the target format is mandatory and never inferred from a filename or ambient
  state;
* an unsupported format is a controlled :class:`SerializationError`.

Headless backend is not required here because these tests never import pyplot
or serialize a Figure; they exercise the resolved policy object only.
"""

from __future__ import annotations

import pytest
from ehp_sn.figures import SerializationError, resolve_serialization_policy


def test_unsupported_serialization_format_is_controlled_error() -> None:
    with pytest.raises(SerializationError):
        resolve_serialization_policy(format="pdf")
    with pytest.raises(SerializationError):
        resolve_serialization_policy(format="gif")


def test_serialization_format_never_inferred() -> None:
    """Serialization requires an explicit format; there is no filename.

    ``resolve_serialization_policy`` requires the format argument; there is no
    path/filename input from which a format could be inferred. An empty/absent
    format is rejected.
    """
    with pytest.raises((SerializationError, TypeError)):
        resolve_serialization_policy()  # missing required format


def test_resolved_policy_records_explicit_parameters() -> None:
    """A resolved policy records its identity-relevant serialization parameters.

    The returned policy must carry the explicit format, DPI, metadata policy,
    and any realization-affecting encoding parameters so that no identity-bearing
    serialization parameter is left implicit (Phase-4 · P4-T3).
    """
    policy = resolve_serialization_policy(format="png", dpi=200, metadata_policy="none")
    assert policy.format == "png"
    assert policy.dpi == 200
    assert "format" in policy.identity_input()
    assert "dpi" in policy.identity_input()


def test_serialization_policy_identity_distinguishes_formats_and_parameters() -> None:
    """A different format or parameter set yields a distinct policy identity."""
    png = resolve_serialization_policy(format="png", dpi=100)
    svg = resolve_serialization_policy(format="svg")
    assert png.identity() != svg.identity()
    high = resolve_serialization_policy(format="png", dpi=300)
    assert png.identity() != high.identity()


# ---------------------------------------------------------------------------
# P4-T12 — visual serialization parameters versus non-visual metadata
# ---------------------------------------------------------------------------


def test_non_visual_metadata_is_not_identity_bearing() -> None:
    """Non-visual file metadata must not change RealizationIdentity (P4-T12).

    ``metadata_policy`` is non-visual file metadata; changing it must not change
    the serialization-policy identity (which carries only visual parameters).
    """
    a = resolve_serialization_policy(format="png", dpi=150, metadata_policy="none")
    b = resolve_serialization_policy(format="png", dpi=150, metadata_policy="embed")
    assert a.identity() == b.identity()


def test_visual_serialization_parameter_is_identity_bearing() -> None:
    """A visual serialization change must change realization identity (P4-T12)."""
    low = resolve_serialization_policy(format="png", dpi=150)
    high = resolve_serialization_policy(format="png", dpi=600)
    assert low.identity() != high.identity()
    png = resolve_serialization_policy(format="png")
    svg = resolve_serialization_policy(format="svg")
    assert png.identity() != svg.identity()


# ---------------------------------------------------------------------------
# P4-T15 — serialization inputs validated before Matplotlib
# ---------------------------------------------------------------------------


def test_invalid_dpi_is_controlled_error() -> None:
    """Invalid DPI is rejected as a controlled error before drawing (P4-T15)."""
    with pytest.raises(SerializationError):
        resolve_serialization_policy(format="png", dpi=-5)
    with pytest.raises(SerializationError):
        resolve_serialization_policy(format="png", dpi=0)


def test_framework_owned_parameter_cannot_be_overridden() -> None:
    """A parameter key owned by the framework must not appear in extra_parameters."""
    with pytest.raises(SerializationError):
        resolve_serialization_policy(format="png", extra_parameters={"format": "svg"}).validate()
    with pytest.raises(SerializationError):
        resolve_serialization_policy(format="png", extra_parameters={"dpi": 300}).validate()
