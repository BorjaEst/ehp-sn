"""Framework-wide content digest primitives.

This module provides the generic digest operations every framework identity and
content-integrity check relies on, defined by ``docs/docs/framework/digests.md``:

* :func:`canonical_digest` — SHA-256 over the exact RFC 8785 (JCS) canonical
  serialization of a JSON-compatible value, reported in the conventional
  ``sha256:<hex>`` form.
* :func:`sha256_bytes_digest` — SHA-256 over the exact serialized bytes of a
  resource, reported in the same conventional ``sha256:<hex>`` form. This is the
  generic byte-content-integrity operation for persisted binary resources that
  are not JSON objects (for example serialized figure bytes).

It is deliberately a mechanism only: it computes a digest of already-given
input and never interprets a producer field. The exact composition of any
particular identity (plan identity, record identity, artifact fingerprint,
resource content digest) is owned by its own framework specification, not here.
"""

from __future__ import annotations

import hashlib
from typing import Any

from .canonicalization import canonicalize

#: Prefix separating a digest algorithm from its hex value, matching the
#: conventional ``sha256:<hex>`` form used across resource descriptors.
_DIGEST_PREFIX = "sha256:"


def canonical_digest(value: Any) -> str:
    """Return the ``sha256:<hex>`` digest of the JCS canonical serialization of ``value``.

    ``value`` must be JSON-compatible; see :func:`canonicalize`. This is the
    generic framework digest operation used by plan identity, record identity,
    and artifact fingerprinting.
    """
    serialized = canonicalize(value)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"{_DIGEST_PREFIX}{digest}"


def sha256_bytes_digest(raw: bytes) -> str:
    """Return the ``sha256:<hex>`` content digest of the exact serialized bytes.

    ``raw`` is the exact resource bytes; the digest is computed directly over
    those bytes (not over any canonical re-serialization). This is the generic
    content-integrity operation for persisted binary content, reused by any
    resource-owning framework contract (including a figure-facing adapter) so
    that no lifecycle stage owns a private hashing algorithm (``rendering.md``
    § "Semantic and byte reproducibility").
    """
    digest = hashlib.sha256(raw).hexdigest()
    return f"{_DIGEST_PREFIX}{digest}"


__all__ = ["canonical_digest", "sha256_bytes_digest"]
