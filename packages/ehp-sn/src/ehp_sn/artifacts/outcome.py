"""The framework domain build outcome (Target 7 / Phase 4C).

This module defines the framework-level result a substrate build returns before
any CLI presents it. It is a **domain result**, not a CLI presentation result:

* it has no exit codes and no CLI categories;
* it exposes only semantic lifecycle outcomes the artifact lifecycle actually
  has — ``committed`` (a newly assembled artifact was committed) and ``reused``
  (an equivalent verified artifact was returned unchanged);
* it does not add speculative statuses such as ``repaired``, ``updated``, or
  ``cached``;
* it does not expose a physical location (the lifecycle is logical-only and the
  framework artifact contract carries no physical location by design).

The CLI may project this result into its own presentation form; it must not
define framework semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .artifact import SubstrateArtifact


@dataclass(frozen=True, slots=True)
class BuildOutcome:
    """The domain outcome of one generic substrate build.

    ``action`` is exactly ``"committed"`` (a freshly assembled artifact was
    committed) or ``"reused"`` (an existing verified artifact with a matching
    build-input identity and artifact fingerprint was returned). ``artifact`` is
    the committed :class:`SubstrateArtifact` for either action.
    """

    action: Literal["committed", "reused"]
    artifact: SubstrateArtifact


__all__ = ["BuildOutcome"]
