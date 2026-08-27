"""Maze-ND immutable source loading, fingerprint verification, and row parsing.

This module owns the Maze-ND side of turning the exact bound source resource
into parsed source problem rows. It deliberately does **not** re-plan, re-resolve
configuration, or reselect a source: it consumes the already-bound exact source
reference (from the framework ``ResolvedResource`` carried in the plan) and the
already-resolved effective :class:`~ehp_research.substrates.maze_nd.configuration.MazeNDConfiguration`
(the opaque session configuration), and fetches exactly that immutable revision.

The fingerprint is the verified content identity of what extraction consumes:
``sha256:`` over the exact served bytes of ``train.jsonl.gz`` followed by
``test.jsonl.gz`` at the pinned revision. The loader re-derives this digest from
the served bytes and fails the build on mismatch, so a changed or tampered
source can never silently produce a different topology collection.

Ownership: source acquisition and verification are Maze-ND concerns. The
framework binds the exact logical reference but (per the resource-requirements
contract) does not itself download or store source bytes; Maze-ND fetches the
pinned immutable revision and verifies it. The network fetch is isolated in
:func:`fetch_revision_file` so the scientific pipeline (fingerprint verification,
decompression, and JSONL parsing) is pure and deterministic-testable without
network access.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import urllib.request
from collections.abc import Iterator

from .configuration import MazeNDConfiguration
from .extraction import ExtractedTopology, extract_row

#: Canonical order of the consumed split files at the pinned revision.
SPLIT_FILES: tuple[str, ...] = ("train.jsonl.gz", "test.jsonl.gz")
#: Split labels derived from file membership (never topology channels).
SPLIT_LABELS: dict[str, str] = {"train.jsonl.gz": "train", "test.jsonl.gz": "test"}


class SourceError(ValueError):
    """A controlled Maze-ND source-loading failure.

    Raised for an unsupported source reference, a fingerprint mismatch, an
    unreadable source, or a malformed JSON row during loading. It is translated
    by the executor into an extraction/import failure diagnostic.
    """


class FingerprintMismatchError(SourceError):
    """The served source bytes do not match the declared content fingerprint.

    This is the controlled failure for "wrong source fingerprint": the build
    must stop rather than produce topologies from unverified content.
    """


def _split_reference(reference: str) -> tuple[str, str]:
    """Split ``huggingface:<org>/<repo>`` into ``(platform, repo_id)``."""
    if ":" not in reference:
        raise SourceError(f"unsupported source reference {reference!r} (missing platform)")
    platform, _, repo = reference.partition(":")
    if platform != "huggingface":
        raise SourceError(f"unsupported source platform {platform!r} in reference {reference!r}")
    if not repo or "/" not in repo:
        raise SourceError(f"invalid huggingface repository in reference {reference!r}")
    return platform, repo


def resolve_url(reference: str, revision: str, filename: str) -> str:
    """Return the immutable source-file URL for the pinned revision.

    The revision comes from the effective configuration carried in the plan; it
    is pinned and immutable, so this is never a mutable "latest" lookup.
    """
    _platform, repo = _split_reference(reference)
    return f"https://huggingface.co/datasets/{repo}/resolve/{revision}/{filename}"


def fetch_revision_file(url: str, *, timeout: float = 120.0) -> bytes:
    """Fetch the exact served bytes of one source file (network seam).

    Isolated so the scientific pipeline can be tested with injected bytes. Raises
    :class:`SourceError` when the file cannot be fetched.
    """
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.read()
    except Exception as exc:  # noqa: BLE001
        raise SourceError(f"failed to fetch source file from {url}: {exc}") from exc


def content_fingerprint(train_bytes: bytes, test_bytes: bytes) -> str:
    """Return ``sha256:<hex>`` over the exact served ``train ++ test`` bytes."""
    digest = hashlib.sha256(train_bytes + test_bytes).hexdigest()
    return f"sha256:{digest}"


def verify_fingerprint(train_bytes: bytes, test_bytes: bytes, expected: str) -> None:
    """Raise :class:`FingerprintMismatchError` unless the served bytes match ``expected``.

    ``expected`` is the configured ``sha256:<hex>``. This is the controlled
    "wrong source fingerprint" failure point.
    """
    actual = content_fingerprint(train_bytes, test_bytes)
    if actual != expected:
        raise FingerprintMismatchError(
            f"source fingerprint mismatch: expected {expected!r}, computed {actual!r} over "
            "the served bytes of train.jsonl.gz ++ test.jsonl.gz at the pinned revision"
        )


def _iter_jsonl(gz_bytes: bytes, split_file: str) -> Iterator[tuple[int, object]]:
    """Decode a gzip JSONL blob, yielding ``(row_ordinal, parsed_row)`` in file order."""
    try:
        decompressed = gzip.decompress(gz_bytes).decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise SourceError(f"source file {split_file!r} is not valid gzip JSONL: {exc}") from exc
    for row_ordinal, line in enumerate(decompressed.splitlines()):
        if not line.strip():
            continue
        try:
            yield row_ordinal, json.loads(line)
        except json.JSONDecodeError as exc:
            raise SourceError(
                f"source file {split_file!r} row {row_ordinal} is not valid JSON: {exc}"
            ) from exc


def iter_source_rows(
    configuration: MazeNDConfiguration,
    resource_source: str,
    train_bytes: bytes,
    test_bytes: bytes,
) -> Iterator[ExtractedTopology]:
    """Yield validated extracted topologies for every selected source row.

    ``resource_source`` is the exact bound source reference from the plan's
    ``ResolvedResource.resource_ref``. It is cross-checked against the effective
    configuration's source reference. Execution uses exactly the source bound
    into the plan.

    Rows are consumed in canonical order — ``train.jsonl.gz`` rows in file order,
    then ``test.jsonl.gz`` rows in file order — for deterministic source
    occurrence identity and stable selection/dedup ordering.
    """
    if resource_source != configuration.source_reference:
        raise SourceError(
            "bound source resource reference "
            f"{resource_source!r} does not match the configured source reference "
            f"{configuration.source_reference!r}"
        )

    verify_fingerprint(train_bytes, test_bytes, configuration.source_fingerprint)

    split_blobs: dict[str, bytes] = {}
    for filename in SPLIT_FILES:
        if filename == "train.jsonl.gz":
            split_blobs[filename] = train_bytes
        else:
            split_blobs[filename] = test_bytes

    for filename in SPLIT_FILES:
        for row_ordinal, row in _iter_jsonl(split_blobs[filename], filename):
            yield extract_row(row, split_file=filename, row_ordinal=row_ordinal)


def load_source(
    configuration: MazeNDConfiguration,
    resource_source: str,
) -> Iterator[ExtractedTopology]:
    """Fetch, verify, and parse the complete selected source population.

    This is the real build path: it resolves the pinned immutable revision from
    the effective configuration, fetches both split files, verifies the content
    fingerprint, and yields validated extracted topologies in canonical order.

    ``resource_source`` is the exact bound source reference from the plan.
    """
    if resource_source != configuration.source_reference:
        raise SourceError(
            "bound source resource reference "
            f"{resource_source!r} does not match the configured source reference "
            f"{configuration.source_reference!r}"
        )
    train_url = resolve_url(
        configuration.source_reference, configuration.source_revision, "train.jsonl.gz"
    )
    test_url = resolve_url(
        configuration.source_reference, configuration.source_revision, "test.jsonl.gz"
    )
    train_bytes = fetch_revision_file(train_url)
    test_bytes = fetch_revision_file(test_url)
    yield from iter_source_rows(configuration, resource_source, train_bytes, test_bytes)


__all__ = [
    "FingerprintMismatchError",
    "SPLIT_FILES",
    "SPLIT_LABELS",
    "SourceError",
    "content_fingerprint",
    "fetch_revision_file",
    "iter_source_rows",
    "load_source",
    "resolve_url",
    "verify_fingerprint",
]
