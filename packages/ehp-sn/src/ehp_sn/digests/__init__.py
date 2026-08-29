"""Framework-wide canonical serialization and content digest primitives.

This package owns the generic mechanism every framework identity digest relies
on: exact RFC 8785 (JCS) canonical serialization of JSON-compatible values and
the ``sha256:<hex>`` digest operation over that canonical serialization.

It is the single framework-wide home for the digest mechanism defined by
``docs/docs/framework/digests.md``. ``digests.md`` remains the authoritative
specification of the algorithm and its integrity semantics; this package
applies it. It is deliberately ownership-neutral with respect to the lifecycle
stages that consume it: plan identity (``ehp_sn.planning``), record identity
(``ehp_sn.execution``), and later artifact fingerprints all digest through this
single mechanism, so no lifecycle stage depends conceptually on another stage's
utility.

Nothing here interprets a producer field, branches on a substrate family, or
imports a concrete research package (``ARCH-001``).
"""

from __future__ import annotations

from .canonicalization import canonicalize
from .digest import canonical_digest, sha256_bytes_digest

__all__ = ["canonical_digest", "canonicalize", "sha256_bytes_digest"]
