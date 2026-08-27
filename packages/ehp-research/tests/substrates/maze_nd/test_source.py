"""Tests for Maze-ND immutable source loading and fingerprint verification.

Covers the exact-source acceptance (same declared source -> same bytes can be
reacquired), verified-source-content -> fingerprint matches, different source
revision -> different identity, the controlled wrong-fingerprint failure, the
bound-resource cross-check, canonical row parsing, and the split-file
membership identity.
"""

from __future__ import annotations

import gzip

import pytest
from ehp_research.substrates.maze_nd.configuration import MazeNDConfiguration
from ehp_research.substrates.maze_nd.source import (
    FingerprintMismatchError,
    SourceError,
    content_fingerprint,
    iter_source_rows,
    resolve_url,
    verify_fingerprint,
)

from . import _fixtures as fx

REVISION = "b1f344fb8d63eea8b602f5bd5ffdd8e146b6595f"
REFERENCE = "huggingface:flaitenberger/maze_hard_augmented"


def _config(**kw) -> MazeNDConfiguration:
    defaults = dict(
        variant="source-topology",
        source_reference=REFERENCE,
        source_revision=kw.get("source_revision", REVISION),
        source_fingerprint=kw.get("source_fingerprint", "sha256:unused"),
        source_schema="maze-nd:extraction/raster/v1",
        source_selection_policy="complete-source",
        selection_before_dedup=True,
        normalization_policy="maze-nd:normalization/raster/v1",
        connectivity_policy="preserve",
        deduplication_policy="maze-nd:dedup/orientation-preserving-raster/v1",
    )
    defaults.update({k: v for k, v in kw.items() if k in defaults})
    return MazeNDConfiguration(**defaults)


def test_fingerprint_stable_for_same_bytes() -> None:
    blob = b"the-same-bytes"
    assert content_fingerprint(blob, blob) == content_fingerprint(blob, blob)
    # Different bytes -> different fingerprint (different source revision/content).
    assert content_fingerprint(b"a", b"b") != content_fingerprint(b"a", b"c")
    assert content_fingerprint(b"a", b"b") != content_fingerprint(b"b", b"a")


def test_sha256_prefix_and_hex() -> None:
    fp = content_fingerprint(b"x", b"y")
    assert fp.startswith("sha256:")
    hexpart = fp[len("sha256:") :]
    assert len(hexpart) == 64
    int(hexpart, 16)


def test_verify_fingerprint_passes_on_match() -> None:
    blob = fx.split_blob([fx.row(fx.grid_from_strings("#S#", "#G#"))])
    expected = content_fingerprint(blob, blob)
    verify_fingerprint(blob, blob, expected)  # should not raise


def test_wrong_fingerprint_raises_controlled_error() -> None:
    blob = fx.split_blob([fx.row(fx.grid_from_strings("#S#", "#G#"))])
    with pytest.raises(FingerprintMismatchError):
        verify_fingerprint(blob, blob, "sha256:" + "0" * 64)


def test_resolve_url_pins_revision() -> None:
    url = resolve_url(REFERENCE, REVISION, "train.jsonl.gz")
    assert REVISION in url
    assert url.endswith("/train.jsonl.gz")
    assert "datasets/flaitenberger/maze_hard_augmented" in url


def test_resolve_url_rejects_unsupported_platform() -> None:
    with pytest.raises(SourceError):
        resolve_url("gitlab:owner/repo", REVISION, "train.jsonl.gz")


def test_iter_source_rows_canonical_order_and_identity() -> None:
    train_blob = fx.split_blob(
        [
            fx.row(fx.grid_from_strings("#S#", "#G#")),
            fx.row(fx.grid_from_strings("# #", "# #")),
        ]
    )
    test_blob = fx.split_blob([fx.row(fx.grid_from_strings("S#", "G#"))])
    cfg = _config(source_fingerprint=content_fingerprint(train_blob, test_blob))
    rows = list(iter_source_rows(cfg, REFERENCE, train_blob, test_blob))

    assert len(rows) == 3
    # canonical order: train rows first (file order), then test rows.
    assert [r.split_file for r in rows] == [
        "train.jsonl.gz",
        "train.jsonl.gz",
        "test.jsonl.gz",
    ]
    assert [r.row_ordinal for r in rows] == [0, 1, 0]


def test_iter_source_rows_cross_checks_bound_reference() -> None:
    train_blob = fx.split_blob([fx.row(fx.grid_from_strings("#S#", "#G#"))])
    test_blob = fx.split_blob([])
    cfg = _config(source_fingerprint=content_fingerprint(train_blob, test_blob))
    with pytest.raises(SourceError):
        list(iter_source_rows(cfg, "huggingface:other/repo", train_blob, test_blob))


def test_malformed_jsonl_is_controlled() -> None:
    train_blob = gzip.compress(b'{"inputs": ')
    test_blob = fx.split_blob([])
    cfg = _config(source_fingerprint=content_fingerprint(train_blob, test_blob))
    with pytest.raises(SourceError):
        list(iter_source_rows(cfg, REFERENCE, train_blob, test_blob))
