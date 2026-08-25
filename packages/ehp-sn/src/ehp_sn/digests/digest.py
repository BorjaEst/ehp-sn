"""Framework-wide content digest over canonical (JCS) serialization.

This module provides the single digest operation every framework identity digest
relies on, defined by ``docs/docs/framework/digests.md`` § "Digest algorithm
and canonical serialization": SHA-256 over the exact RFC 8785 (JCS) canonical
serialization of a JSON-compatible value, reported in the conventional
``sha256:<hex>`` form.

It is deliberately a mechanism only: it computes a digest of already-canonical
input and never interprets a producer field. The exact composition of any
particular identity (plan identity, record identity, artifact fingerprint) is
owned by its own framework specification, not here.
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


__all__ = ["canonical_digest"]
