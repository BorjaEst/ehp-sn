"""Figure-persistence boundary tests for :mod:`ehp_sn.figures.persistence`.

These validate the Phase-4 persistence seam (Phase 4B). Phase 4B waits for a
real persistent resource owner; the framework must not invent a figure-specific
persistence system. The only generic, owner-agnostic helper is content-integrity
verification: that a realized figure's serialized bytes reproduce their recorded
``sha256:`` content digest (``rendering.md`` § "Semantic and byte
reproducibility"; Phase-4 § 10/§ 16, P4-11).

Headless backend is required because these tests realize a projection to obtain
serialized bytes.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless backend required

import pytest
from ehp_sn.digests import sha256_bytes_digest
from ehp_sn.figures import (
    FigureContentIntegrityError,
    effective_figure_registry,
    prepare_figure,
    realize_projection,
    resolve_serialization_policy,
    verify_content_digest,
)
from ehp_sn.figures.realization import RealizedFigure
from ehp_sn.figures.service import _ExactSource

_FIGURE_REF = "figure:raster-topology-inspection/v1"


def _source(*, record_id: str = "sha256:AAA") -> _ExactSource:
    return _ExactSource(
        artifact_ref="artifact:dg/v1",
        record_id=record_id,
        schema_ref="raster-topology/v1",
        content={
            "domain": {"height": 3, "width": 4, "position_count": 12},
            "passable": [True] * 12,
        },
    )


def _realized_png():
    reg = effective_figure_registry()
    projection = prepare_figure(reg, _FIGURE_REF, _source())
    return realize_projection(
        projection, serialization=resolve_serialization_policy(format="png"), registry=reg
    )


def _mutated_bytes(r: RealizedFigure) -> bytes:
    """Return a mutated copy of the serialized bytes (flip one byte)."""
    data = bytearray(r.bytes)
    data[0] ^= 0xFF
    return bytes(data)


def test_content_integrity_verification() -> None:
    r = _realized_png()
    verify_content_digest(r)  # does not raise


def test_content_integrity_verification_detects_corruption() -> None:
    r = _realized_png()
    corrupted = _mutated_bytes(r)
    assert corrupted != r.bytes
    bad = RealizedFigure(
        format=r.format,
        bytes=corrupted,
        content_digest=r.content_digest,
        realization_identity=r.realization_identity,
        environment=r.environment,
    )
    with pytest.raises(FigureContentIntegrityError):
        verify_content_digest(bad)


# ---------------------------------------------------------------------------
# P4-T13 — content integrity reuses the generic EHP-SN digest mechanism
# ---------------------------------------------------------------------------


def test_content_digest_uses_generic_framework_byte_digest() -> None:
    """A realized figure's digest equals the generic framework byte digest.

    The figure layer is a thin adapter over ``ehp_sn.digests.sha256_bytes_digest``;
    it owns no hashing algorithm (P4-T13).
    """
    r = _realized_png()
    assert r.content_digest.value == sha256_bytes_digest(r.bytes)


def test_verify_content_digest_reuses_generic_mechanism() -> None:
    """verify_content_digest recomputes through the generic digest (P4-T13).

    Corrupting the bytes changes the generic digest, which the figure-facing
    adapter detects.
    """
    r = _realized_png()
    corrupted = _mutated_bytes(r)
    assert sha256_bytes_digest(corrupted) != r.content_digest.value
    bad = RealizedFigure(
        format=r.format,
        bytes=corrupted,
        content_digest=r.content_digest,
        realization_identity=r.realization_identity,
        environment=r.environment,
    )
    with pytest.raises(FigureContentIntegrityError):
        verify_content_digest(bad)
