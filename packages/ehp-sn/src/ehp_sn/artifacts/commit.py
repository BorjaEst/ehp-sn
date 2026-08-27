"""Reuse, conflict, and durable publication of a substrate data artifact.

This module owns the framework publication decision and the durable commit step:

* **reuse** — an existing committed artifact whose build-input identity *and*
  artifact fingerprint match the assembled candidate is returned unchanged
  (deterministic reuse). Reuse never modifies provenance and returns the
  existing logical reference (``data-artifacts.md`` § "Reuse").
* **conflict** — a committed artifact that shares a build-input identity but
  differs in fingerprint, or occupies the same immutable release coordinate with
  different content, is a controlled conflict: the build fails rather than
  publishing accidentally.
* **publish** — a freshly assembled candidate is durably published to its
  configured release coordinate through isolated staging, integrity
  verification, and an atomic final transition. Only this establishes the
  ``committed`` outcome (Target 12): an :class:`AssembledArtifact` alone is
  "assembled", never "committed".

The producer never participates in conflict resolution and never supplies the
final path; the artifact lifecycle is the sole release-coordinate authority.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from ehp_sn.planning import ReleaseCoordinate

from .artifact import SubstrateArtifact
from .assembly import AssembledArtifact
from .resolve import load_release
from .store import (
    StoreError,
    cleanup_staging,
    finalize_manifest,
    inspect_release,
    publish_release,
    release_path,
    stage_release,
    verify_staged,
)


class CommitConflictError(Exception):
    """A committed artifact occupies the target with different content.

    Raised when publication would overwrite or diverge from a committed
    artifact: an existing committed artifact shares the candidate's build-input
    identity but differs in fingerprint, or the immutable release coordinate is
    already occupied by different content. The operation must fail rather than
    publish a second authoritative release.
    """


class InvalidExistingStateError(Exception):
    """The destination contains incomplete or corrupt content.

    Raised when the destination at the selected release coordinate is not a
    valid committed artifact and cannot be treated as either reusable or safely
    available. Removal/replacement is permitted only under the explicit
    incomplete-state policy; a committed valid release is never replaced.
    """


class ReleaseNotConfiguredError(Exception):
    """The build has no configured release coordinate to publish to.

    Raised when the framework cannot resolve an explicit release coordinate
    (the configuration declares no release number, or the producer declares no
    variant). The framework never auto-assigns a release number.
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
    published fresh.
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


def publish_artifact(
    candidate: AssembledArtifact,
    *,
    root: Path,
    coordinate: ReleaseCoordinate,
) -> SubstrateArtifact:
    """Durably publish a fully assembled candidate to its configured release.

    Crosses the persistence boundary: writes the assembled candidate into an
    isolated framework staging area, finalizes the manifest, verifies the staged
    candidate, and atomically publishes it to the configured release coordinate,
    returning the durable committed :class:`SubstrateArtifact`.

    The framework never auto-assigns a release: ``coordinate`` is the explicit
    configured coordinate. If a committed valid artifact already occupies the
    coordinate, callers should resolve reuse first; if different content
    occupies it, publication raises :class:`CommitConflictError` (never
    overwriting an immutable release).
    """
    existing = inspect_release(root, coordinate)
    if existing.committed_exists and existing.valid:
        existing_artifact = load_release(release_path(root, coordinate))
        if (
            existing.build_input_identity == candidate.build_input_identity
            and existing_artifact.artifact_fingerprint == candidate.artifact_fingerprint
        ):
            # Equivalent verified artifact already committed at the coordinate.
            return existing_artifact
        raise CommitConflictError(
            f"release coordinate {coordinate.name!r} v{coordinate.release} already "
            "commits different content; refusing to overwrite an immutable release"
        )
    if existing.committed_exists and not existing.valid:
        raise InvalidExistingStateError(
            f"release coordinate {coordinate.name!r} v{coordinate.release} contains "
            "incomplete or corrupt content; it cannot be treated as committed or safely "
            "available"
        )

    staging, resource_paths = stage_release(root, coordinate, candidate)
    try:
        finalize_manifest(
            assembled=candidate,
            coordinate=coordinate,
            staging=staging,
            resource_paths=resource_paths,
        )
        verify_staged(staging)
        publish_release(root, coordinate, staging)
    except StoreError:
        cleanup_staging(staging)
        raise
    except Exception:
        cleanup_staging(staging)
        raise

    return load_release(release_path(root, coordinate))


__all__ = [
    "CommitConflictError",
    "InvalidExistingStateError",
    "ReleaseNotConfiguredError",
    "find_reusable",
    "publish_artifact",
]
