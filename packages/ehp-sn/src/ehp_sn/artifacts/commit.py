"""Reuse, conflict, and logical commit of a substrate data artifact.

This module implements the framework-owned decision and commit semantics for the
"correctness of edition" lifecycle:

* **reuse** — an existing committed artifact whose build-input identity *and*
  artifact fingerprint match the assembled candidate is returned unchanged
  (deterministic reuse). Reuse never modifies provenance and returns the
  existing logical reference (``docs/docs/framework/artifacts.md`` § "Reuse").
* **conflict** — an existing committed artifact that shares a build-input
  identity but differs in fingerprint indicates the destination is occupied by
  incompatible content; the build fails rather than publishing accidentally
  (``data-artifacts.md`` § "Planning states").
* **commit** — a freshly assembled candidate is frozen into an immutable
  committed ``SubstrateArtifact`` only after full assembly and fingerprinting
  succeed. A failed or partial build never yields an artifact that discovery
  treats as valid.

Release-number allocation and physical coordinates are out of scope by design
("no release, no git"); identity matching is based on framework identity/artifact
semantics, never filename equality. The framework never invokes the producer
during classification or commit.
"""

from __future__ import annotations

from collections.abc import Iterable

from .artifact import SubstrateArtifact
from .assembly import AssembledArtifact


class CommitConflictError(Exception):
    """A committed artifact occupies a build-input identity with different content.

    Raised when an existing committed artifact shares the candidate's
    build-input identity but differs in artifact fingerprint (or otherwise
    carries incompatible content). The operation must fail rather than
    accidentally publish a second authoritative release.
    """


def find_reusable(
    existing: Iterable[SubstrateArtifact],
    candidate: AssembledArtifact,
) -> SubstrateArtifact | None:
    """Return an existing committed artifact deterministically reusable for ``candidate``.

    An existing artifact is reusable when its build-input identity **and** its
    artifact fingerprint both match the candidate's. Reuse is based on framework
    identity/artifact semantics, never on filename or coordinate equality. When
    an existing artifact shares the build-input identity but has a *different*
    fingerprint, that is a conflict and raises :class:`CommitConflictError`.
    Returns ``None`` when no existing artifact matches and the candidate must be
    committed fresh.
    """
    reusable: SubstrateArtifact | None = None
    for artifact in existing:
        if artifact.build_input_identity != candidate.build_input_identity:
            continue
        if artifact.artifact_fingerprint == candidate.artifact_fingerprint:
            # Equivalent verified artifact — reuse (first match wins).
            if reusable is None:
                reusable = artifact
            continue
        if reusable is None:
            raise CommitConflictError(
                f"build-input identity {candidate.build_input_identity!r} is committed "
                "with a different artifact fingerprint; refusing to publish conflicting "
                "content"
            )
    return reusable


def commit_artifact(candidate: AssembledArtifact) -> SubstrateArtifact:
    """Freeze a fully assembled, identified candidate into a committed artifact.

    The candidate must already be fully assembled and fingerprinted (produced by
    :func:`~ehp_sn.artifacts.assembly.assemble_artifact`). Commit is logical and
    atomic: it constructs one immutable ``SubstrateArtifact`` from the complete
    candidate, so no partial state is ever observable as a valid committed
    artifact. The producer is never called here.
    """
    return SubstrateArtifact(assembly=candidate)


__all__ = ["CommitConflictError", "commit_artifact", "find_reusable"]
