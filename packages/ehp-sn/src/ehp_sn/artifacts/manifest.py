"""Physical artifact manifest for a committed substrate release.

This module defines the authoritative physical manifest of a committed release
(``data-artifacts.md`` § "Manifest, configuration, and provenance authority" and
``manifests.md``). It is the durable, on-disk descriptor that records:

* the committed release coordinate and artifact reference;
* the build-input identity and artifact fingerprint;
* the declared logical resources with their relative physical locations,
  resource kind, identity-bearing status, and content digests.

The manifest is JSON (``manifest.json``) under a versioned schema. It identifies
the authoritative resource roles and their relative locations; directory and
file names alone are never authoritative (``data-layout.md`` § "interim/").

The manifest is written as the final resource during publication and is read to
resolve, verify, and reuse a committed release.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from ehp_sn.planning import ReleaseCoordinate

from .assembly import AssembledArtifact
from .descriptors import LogicalResourceDescriptor

#: Canonical logical resource names of the framework-declared resources.
_MANIFEST_RESOURCE = "manifest"
_PAYLOADS_RESOURCE = "payloads"
_INDEX_RESOURCE = "index"
_RESOLVED_CONFIG_RESOURCE = "resolved-config"
_PROVENANCE_RESOURCE = "provenance"

#: Manifest schema version.
MANIFEST_SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class ManifestResource:
    """One manifest-declared resource of a committed release.

    Mirrors :class:`LogicalResourceDescriptor` plus the durable relative
    physical location where the resource is stored. ``identity_bearing`` marks
    whether the resource participates in the artifact fingerprint.
    """

    name: str
    resource_kind: str
    relative_path: str
    schema_ref: str | None
    identity_bearing: bool
    digest: str


class ManifestParseError(Exception):
    """A manifest file is malformed, unsupported, or incomplete."""


def _resource_relative_path(resource: LogicalResourceDescriptor) -> str:
    """Return the relative physical file for a declared logical resource.

    Generic over logical resource content: each declared logical resource is
    persisted under a ``resources/`` directory, named by its logical resource
    name. Adding a new logical resource requires no publisher code change.
    """
    return f"resources/{resource.name}.data"


def build_manifest(
    *,
    assembled: AssembledArtifact,
    coordinate: ReleaseCoordinate,
    resource_paths: dict[str, str],
) -> dict[str, Any]:
    """Construct the physical manifest document for a release.

    ``resource_paths`` maps each logical resource name (including the
    framework-declared resources) to its relative physical path. The manifest
    records the coordinate, artifact reference name, build-input identity,
    artifact fingerprint, artifact-kind, component/spec references, and every
    declared resource descriptor with its relative location and digest.
    """
    resources: list[dict[str, Any]] = []
    for resource in assembled.resources:
        rel = resource_paths[resource.name]
        resources.append(
            {
                "name": resource.name,
                "resource_kind": resource.resource_kind,
                "relative_path": rel,
                "schema_ref": resource.schema_ref,
                "identity_bearing": resource.identity_bearing,
                "digest": resource.digest,
            }
        )
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "artifact_kind": "substrate",
        "component_ref": assembled.component_ref,
        "output_contract": assembled.output_contract,
        "release": {
            "family": coordinate.family,
            "variant": coordinate.variant,
            "release": coordinate.release,
            "version": coordinate.version,
        },
        "artifact_name": coordinate.name,
        "build_input_identity": assembled.build_input_identity,
        "artifact_fingerprint": assembled.artifact_fingerprint,
        "resources": resources,
    }


def serialize_manifest(document: dict[str, Any]) -> bytes:
    """Serialize a manifest document to canonical JSON bytes."""
    return json.dumps(document, sort_keys=True, separators=(",", ":")).encode("utf-8")


def parse_manifest(raw: bytes) -> dict[str, Any]:
    """Parse and validate a manifest document from its serialized bytes."""
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManifestParseError(f"manifest is not valid JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise ManifestParseError("manifest must be a JSON object")
    if document.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise ManifestParseError(
            f"unsupported manifest schema version: {document.get('schema_version')!r}"
        )
    return document


def manifest_coordinate(document: dict[str, Any]) -> ReleaseCoordinate:
    """Return the release coordinate recorded by a manifest document."""
    release = document.get("release")
    if not isinstance(release, dict):
        raise ManifestParseError("manifest records no release coordinate")
    try:
        return ReleaseCoordinate(
            family=release["family"],
            variant=release["variant"],
            release=int(release["release"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ManifestParseError(f"manifest release coordinate is malformed: {exc}") from exc


def manifest_resources(document: dict[str, Any]) -> tuple[ManifestResource, ...]:
    """Return the manifest-declared resources as durable descriptors."""
    raw: Any = document.get("resources")
    if not isinstance(raw, list):
        raise ManifestParseError("manifest records no resources")
    entries: list[ManifestResource] = []
    for entry in raw:
        if not isinstance(entry, dict):
            raise ManifestParseError("manifest resource entry must be an object")
        try:
            entries.append(
                ManifestResource(
                    name=entry["name"],
                    resource_kind=entry["resource_kind"],
                    relative_path=entry["relative_path"],
                    schema_ref=entry.get("schema_ref"),
                    identity_bearing=bool(entry["identity_bearing"]),
                    digest=entry["digest"],
                )
            )
        except KeyError as exc:
            raise ManifestParseError(f"manifest resource entry is incomplete: missing {exc}") from exc
    return tuple(entries)


__all__ = [
    "MANIFEST_SCHEMA_VERSION",
    "ManifestParseError",
    "ManifestResource",
    "build_manifest",
    "manifest_coordinate",
    "manifest_resources",
    "parse_manifest",
    "serialize_manifest",
]
