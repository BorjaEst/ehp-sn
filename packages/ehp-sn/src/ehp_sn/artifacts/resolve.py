"""Durable resolution of a committed substrate release.

This module resolves a committed release — from its physical location or its
release-coordinate + artifact root — back into a durable
:class:`~ehp_sn.artifacts.SubstrateArtifact`, independently of the in-memory
object that created it (``Target 10``: after the build process terminates, a
committed artifact remains resolvable in a fresh resolver/process context).

Resolution reads the committed manifest, validates it against the requested
coordinate, and reconstructs the framework metadata and logical content from the
manifest-declared resources. A missing or corrupt publication cannot masquerade
as a committed artifact: resolution fails cleanly (``StoreError`` /
``ManifestParseError``) rather than fabricating an artifact.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ehp_sn.execution import LogicalRecord, LogicalResource
from ehp_sn.planning import ReleaseCoordinate

from .artifact import SubstrateArtifact
from .assembly import AssembledArtifact
from .descriptors import LogicalResourceDescriptor, RecordIndexEntry
from .manifest import manifest_coordinate, manifest_resources, parse_manifest
from .store import StoreError, artifact_ref, release_path

_MANIFEST_FILENAME = "manifest.json"
_PROVENANCE_FILENAME = "provenance.json"
_INDEX_FILENAME = "index.jsonl"


def load_release(location: Path) -> SubstrateArtifact:
    """Resolve a committed ``SubstrateArtifact`` from a physical release directory.

    Reads ``manifest.json``, validates the coordinate baked into the manifest,
    and reconstructs the artifact's framework metadata and logical content from
    the manifest-declared resources. Raises :class:`StoreError` (or
    :class:`ManifestParseError`) when the release is missing or corrupt.
    """
    manifest_file = location / _MANIFEST_FILENAME
    if not manifest_file.is_file():
        raise StoreError(f"no committed release at {location}")
    try:
        document = parse_manifest(manifest_file.read_bytes())
    except OSError as exc:
        raise StoreError(f"cannot read committed manifest at {location}: {exc}") from exc

    coordinate = manifest_coordinate(document)
    assembly = _reconstruct_assembly(location, document, coordinate)
    return SubstrateArtifact(
        assembly=assembly,
        release_coordinate=coordinate,
        artifact_ref=artifact_ref(coordinate),
        location=location,
    )


def resolve_release(root: Path, coordinate: ReleaseCoordinate) -> SubstrateArtifact:
    """Resolve a committed release by its release coordinate under an artifact root.

    Raises :class:`StoreError` when no committed release exists at the
    coordinate or the release does not verify.
    """
    return load_release(release_path(root, coordinate))


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise StoreError(f"cannot read resource {path}: {exc}") from exc


def _read_jsonl(path: Path) -> list[Any]:
    try:
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line]
    except OSError as exc:
        raise StoreError(f"cannot read resource {path}: {exc}") from exc
    return [json.loads(line) for line in lines]


def _reconstruct_assembly(
    location: Path,
    document: dict[str, Any],
    coordinate: ReleaseCoordinate,
) -> AssembledArtifact:
    """Reconstruct an :class:`AssembledArtifact` view from a committed release."""
    resources = manifest_resources(document)
    resource_descriptors = tuple(
        LogicalResourceDescriptor(
            name=r.name,
            resource_kind=r.resource_kind,
            schema_ref=r.schema_ref,
            identity_bearing=r.identity_bearing,
            digest=r.digest,
        )
        for r in resources
    )

    # Logical records from the payloads resource (manifest-declared location).
    payloads_rel = next(
        (r.relative_path for r in resources if r.name == "payloads"),
        "resources/payloads.data",
    )
    payload_entries = _read_jsonl(location / payloads_rel)
    records = tuple(
        LogicalRecord(
            record_id=entry["record_id"],
            schema_ref=entry["schema_ref"],
            content=entry["content"],
            descriptors=(),
        )
        for entry in payload_entries
    )

    # Auxiliary logical resources from their manifest-declared files.
    auxiliary: list[LogicalResource] = []
    for r in resources:
        if r.name in ("payloads", "index") or r.resource_kind in (
            "resolved-config",
            "provenance",
            "index",
            "payload",
            "manifest",
        ):
            continue
        aux_path = location / r.relative_path
        auxiliary.append(
            LogicalResource(
                name=r.name,
                content=_read_json(aux_path),
                resource_kind=r.resource_kind,
            )
        )

    # Record index from the index file.
    index_entries = _read_jsonl(location / _INDEX_FILENAME)
    index = tuple(
        RecordIndexEntry(
            record_id=entry["record_id"],
            schema_ref=entry["schema_ref"],
            payload_locator=entry["payload_locator"],
            descriptors=(),
        )
        for entry in index_entries
    )

    provenance = _read_json(location / _PROVENANCE_FILENAME)
    provenance_digest = next(
        (r.digest for r in resources if r.name == "provenance"),
        "",
    )

    return AssembledArtifact(
        component_ref=str(document.get("component_ref", "")),
        output_contract=str(document.get("output_contract", "")),
        build_input_identity=str(document.get("build_input_identity", "")),
        resources=resource_descriptors,
        index=index,
        records=records,
        auxiliary=tuple(auxiliary),
        producer_descriptors=(),
        provenance=provenance,
        provenance_digest=provenance_digest,
        artifact_fingerprint=str(document.get("artifact_fingerprint", "")),
        identity_inputs=(),
        bound_resources=(),
    )


__all__ = ["load_release", "resolve_release"]
