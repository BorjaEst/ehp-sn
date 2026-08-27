"""Monorepo filesystem artifact store for committed substrate releases.

This module is the framework-owned physical publication backend for the
demonstrated requirement (a workspace filesystem backend under
``data/interim/<family>/<variant>/v<N>/``; ``data-layout.md`` § "interim/" and
``data-artifacts.md`` § "Conventional release coordinates").

It owns generic artifact persistence — release-coordinate resolution, existing-
state inspection, isolated staging, deterministic serialization of framework
logical resources, integrity verification, atomic publication, and durable
resolution. It must not know:

```text
one family's graph semantics
another family's lineage semantics
a third family's vocabulary semantics
a fourth family's retry semantics
```

Adding a new logical resource type requires no store code change: the store
persists declared logical resources generically. There are no substrate-family
branches.

The store is a physical backend, not a plugin or store abstraction: the
demonstrated requirement is a workspace filesystem publication, so this module
implements exactly that and nothing more (no S3, no database, no remote
backend).
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ehp_sn.digests import canonical_digest
from ehp_sn.execution import LogicalRecord, LogicalResource
from ehp_sn.planning import ReleaseCoordinate

from .assembly import AssembledArtifact
from .manifest import (
    ManifestParseError,
    build_manifest,
    manifest_coordinate,
    manifest_resources,
    parse_manifest,
    serialize_manifest,
)

#: Canonical framework-declared logical resource names.
_PAYLOADS_RESOURCE = "payloads"
_INDEX_RESOURCE = "index"
_RESOLVED_CONFIG_RESOURCE = "resolved-config"
_PROVENANCE_RESOURCE = "provenance"
_MANIFEST_RESOURCE = "manifest"

#: Conventional physical filenames for the top-level framework resources.
_MANIFEST_FILENAME = "manifest.json"
_CONFIG_FILENAME = "config.resolved.toml"
_PROVENANCE_FILENAME = "provenance.json"
_INDEX_FILENAME = "index.jsonl"

#: Subdirectory under a staged/final release that holds logical resource files.
_RESOURCES_DIR = "resources"


class StoreError(Exception):
    """A controlled framework artifact-store failure.

    Raised for physical publication/integrity conditions (unwritable
    destination, corrupt existing release, atomic-publication failure). It is a
    framework-domain error, not a CLI category; the CLI maps it at its own layer.
    """


@dataclass(frozen=True, slots=True)
class ExistingState:
    """The physical existing-state facts of one release coordinate.

    ``committed_exists`` is whether a manifest records a committed release at
    the coordinate; ``valid`` whether that release passes structural integrity
    inspection (manifest present and parseable; declared resources present and
    digest-consistent); ``build_input_identity`` is the recorded build-input
    identity of the committed release when one is present and readable, else
    ``None``.
    """

    committed_exists: bool
    valid: bool
    build_input_identity: str | None


def artifact_ref(coordinate: ReleaseCoordinate) -> str:
    """Return the canonical artifact reference of a release coordinate.

    Follows the release-coordinate ``artifact:`` reference grammar
    (``references.md``): ``artifact:<name>/v<N>`` where the ``name`` segment is
    the release coordinate name ``<family>/<variant>`` — for example
    ``artifact:<family>/<variant>/v1``.
    """
    return f"artifact:{coordinate.name}/v{coordinate.release}"


def release_path(root: Path, coordinate: ReleaseCoordinate) -> Path:
    """Return the physical path of a release coordinate under an artifact root.

    ``root`` is the base directory that directly contains the family segment
    (the "interim-data root"); the physical release is
    ``<root>/<family>/<variant>/v<release>/``.
    """
    return root / coordinate.family / coordinate.variant / coordinate.version


def inspect_release(root: Path, coordinate: ReleaseCoordinate) -> ExistingState:
    """Inspect the physical existing state of a release coordinate (read-only).

    Determines whether a committed artifact occupies the coordinate and whether
    it passes structural integrity inspection (manifest present/parseable and
    declared resources digest-consistent). Creating nothing; purely read-only.
    """
    path = release_path(root, coordinate)
    manifest_file = path / _MANIFEST_FILENAME
    if not manifest_file.is_file():
        return ExistingState(committed_exists=False, valid=True, build_input_identity=None)
    try:
        document = parse_manifest(manifest_file.read_bytes())
    except (OSError, ManifestParseError):
        return ExistingState(committed_exists=True, valid=False, build_input_identity=None)
    recorded = manifest_coordinate(document)
    if recorded != coordinate:
        return ExistingState(committed_exists=True, valid=False, build_input_identity=None)
    if not _resources_verify(path, document):
        return ExistingState(committed_exists=True, valid=False, build_input_identity=None)
    return ExistingState(
        committed_exists=True,
        valid=True,
        build_input_identity=document.get("build_input_identity"),
    )


def _resources_verify(release_dir: Path, document: dict[str, Any]) -> bool:
    """Return whether every declared resource exists and matches its digest.

    Read-only integrity inspection: all manifest-declared resources must be
    present and their persisted content must reproduce the declared digest. Used
    to classify existing state as valid (reusable/conflict) vs invalid
    (incomplete/corrupt), and during staged verification.
    """
    try:
        for resource in manifest_resources(document):
            rel = release_dir / resource.relative_path
            if not rel.is_file():
                return False
            if _file_digest(rel, resource.name) != resource.digest:
                return False
    except (OSError, StoreError):
        return False
    return True


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _write_bytes(path: Path, data: bytes) -> None:
    path.write_bytes(data)


def _serialize_records(records: tuple[LogicalRecord, ...]) -> str:
    """Serialize record payloads (one JSON object per line)."""
    lines = [
        json.dumps(
            {
                "record_id": record.record_id,
                "schema_ref": record.schema_ref,
                "descriptors": [{"name": d.name, "value": d.value} for d in record.descriptors],
                "content": record.content,
            },
            sort_keys=True,
        )
        for record in records
    ]
    return "\n".join(lines) + ("\n" if lines else "")


def _serialize_index(assembled: AssembledArtifact) -> str:
    """Serialize the record index (one JSON object per line)."""
    lines = [
        json.dumps(
            {
                "record_id": entry.record_id,
                "schema_ref": entry.schema_ref,
                "payload_locator": entry.payload_locator,
            },
            sort_keys=True,
        )
        for entry in assembled.index
    ]
    return "\n".join(lines) + ("\n" if lines else "")


def _serialize_resolved_config(assembled: AssembledArtifact) -> str:
    """Serialize the framework-visible resolved-configuration representation.

    Mirrors the exact structure digested during assembly
    (``assembly._resolved_config_digest``) so the persisted file's re-parsed
    content reproduces the declared resolved-config digest.
    """
    identity_inputs = [{"name": item.name, "value": item.value} for item in assembled.identity_inputs]
    resources = [
        {
            "requirement_ref": resource.requirement_ref,
            "resource_ref": resource.resource_ref,
            "resolution_source": resource.resolution_source,
        }
        for resource in assembled.bound_resources
    ]
    document = {"identity_inputs": identity_inputs, "resources": resources}
    # Preserve logical structure; TOML is the conventional resolved-config form.
    return _dict_to_toml(document)


def _dict_to_toml(document: dict[str, Any]) -> str:
    """Serialize a small framework-owned dict to TOML text (deterministic)."""
    import tomli_w

    return tomli_w.dumps(document)


def _serialize_auxiliary(resource: LogicalResource) -> str:
    """Serialize one auxiliary logical resource's opaque content as JSON."""
    return json.dumps(resource.content, sort_keys=True, default=str)


def _serialize_provenance(assembled: AssembledArtifact) -> str:
    """Serialize the provenance resource as JSON."""
    return json.dumps(assembled.provenance, sort_keys=True, default=str)


def stage_release(
    root: Path, coordinate: ReleaseCoordinate, assembled: AssembledArtifact
) -> tuple[Path, dict[str, str]]:
    """Serialize an assembled artifact into an isolated publication staging dir.

    Writes every declared logical resource into a framework-controlled temporary
    area under ``root`` and returns the staging directory and a mapping of
    logical resource name → relative physical path. The manifest is deliberately
    NOT written here (it is finalized with the resource paths and written at the
    end of publication). Creating a partial *release* path is avoided: staging
    lives under a hidden framework temp coordinate that never appears to be a
    committed release (``data-layout.md`` "Temporary staging directories").
    """
    root.mkdir(parents=True, exist_ok=True)
    staging = _create_staging_dir(root)
    resources_dir = staging / _RESOURCES_DIR
    resources_dir.mkdir(parents=True, exist_ok=True)

    # index
    index_file = staging / _INDEX_FILENAME
    _write_text(index_file, _serialize_index(assembled))

    # resolved configuration
    config_file = staging / _CONFIG_FILENAME
    _write_text(config_file, _serialize_resolved_config(assembled))

    # provenance
    provenance_file = staging / _PROVENANCE_FILENAME
    _write_text(provenance_file, _serialize_provenance(assembled))

    # payloads + auxiliary logical resources live under resources/
    _write_text(resources_dir / f"{_PAYLOADS_RESOURCE}.data", _serialize_records(assembled.records))

    resource_paths: dict[str, str] = {}
    for resource in assembled.auxiliary:
        rel = os.path.join(_RESOURCES_DIR, f"{resource.name}.data")
        _write_text(resources_dir / f"{resource.name}.data", _serialize_auxiliary(resource))
        resource_paths[resource.name] = rel

    return staging, resource_paths


def _create_staging_dir(root: Path) -> Path:
    """Create a framework-controlled temporary publication area under ``root``.

    The staging name is a hidden, non-release-looking directory (never
    ``<family>/<variant>/v<N>/``) so a mid-publication failure cannot be
    mistaken for a committed release.
    """
    return Path(tempfile.mkdtemp(prefix=".staging-", dir=str(root)))


def finalize_manifest(
    *,
    assembled: AssembledArtifact,
    coordinate: ReleaseCoordinate,
    staging: Path,
    resource_paths: dict[str, str],
) -> Path:
    """Write the manifest into the staging dir and return its path."""
    document = build_manifest(
        assembled=assembled,
        coordinate=coordinate,
        resource_paths={**_all_resource_paths(assembled, resource_paths)},
    )
    manifest_file = staging / _MANIFEST_FILENAME
    _write_bytes(manifest_file, serialize_manifest(document))
    return manifest_file


def _all_resource_paths(assembled: AssembledArtifact, resource_paths: dict[str, str]) -> dict[str, str]:
    """Merge the framework top-level resource paths with the logical paths."""
    paths: dict[str, str] = {
        _MANIFEST_RESOURCE: _MANIFEST_FILENAME,
        _PAYLOADS_RESOURCE: os.path.join(_RESOURCES_DIR, f"{_PAYLOADS_RESOURCE}.data"),
        _INDEX_RESOURCE: _INDEX_FILENAME,
        _RESOLVED_CONFIG_RESOURCE: _CONFIG_FILENAME,
        _PROVENANCE_RESOURCE: _PROVENANCE_FILENAME,
    }
    paths.update(resource_paths)
    return paths


def verify_staged(staging: Path) -> None:
    """Verify a staged release candidate before publication (publication integrity).

    Checks that the manifest is present and parseable and that the payload
    resources' persisted files reproduce the digests declared in the manifest
    (``data-artifacts.md`` § "Validation"). This is *publication* integrity "did
    we persist exactly the assembled artifact correctly?" — it is not the future
    full scientific ``data validate`` subsystem.
    """
    manifest_file = staging / _MANIFEST_FILENAME
    if not manifest_file.is_file():
        raise StoreError("staged release has no manifest")
    try:
        document = parse_manifest(manifest_file.read_bytes())
    except OSError as exc:
        raise StoreError(f"cannot read staged manifest: {exc}") from exc
    except ManifestParseError as exc:
        raise StoreError(f"staged manifest is invalid: {exc}") from exc

    # Every manifest-declared resource exists.
    declared = manifest_resources(document)
    for resource in declared:
        rel = Path(staging) / resource.relative_path
        if not rel.is_file():
            raise StoreError(f"staged release missing declared resource {resource.name!r}")

    # Serialized-resource digest agreement for the framework top-level resources
    # (payloads, index, resolved-config, provenance) and auxiliary resources.
    d = manifest_resources(document)
    for resource in d:
        expected = resource.digest
        actual = _file_digest(Path(staging) / resource.relative_path, resource.name)
        if actual != expected:
            raise StoreError(
                f"staged resource {resource.name!r} digest mismatch: expected {expected}, got {actual}"
            )


def _file_digest(path: Path, name: str) -> str:
    """Recompute a persisted resource's digest from its on-disk bytes."""
    raw = path.read_bytes()
    try:
        if name in (_PAYLOADS_RESOURCE, _INDEX_RESOURCE):
            # payloads and index are line-delimited JSON objects.
            content: object = [_jsonl_line(line) for line in raw.decode("utf-8").splitlines() if line]
        elif name == _RESOLVED_CONFIG_RESOURCE:
            import tomllib

            content = tomllib.loads(raw.decode("utf-8"))
        else:
            # provenance and auxiliary/generic logical resources are JSON content.
            content = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise StoreError(f"cannot reparse staged resource {name!r}: {exc}") from exc
    return canonical_digest(content)


def _jsonl_line(line: str) -> Any:
    import json as _json

    return _json.loads(line)


def publish_release(
    root: Path,
    coordinate: ReleaseCoordinate,
    staging: Path,
) -> Path:
    """Atomically publish a verified staged release to its final coordinate.

    The final coordinate is created only from a complete, verified staging
    directory. The rename is atomic within the same filesystem, so a failure
    before this point never leaves a partially committed release at the final
    coordinate, and an existing committed coordinate is never overwritten
    (``data-artifacts.md`` § "Published-coordinate immutability").
    """
    final = release_path(root, coordinate)
    final.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.rename(staging, final)
    except OSError as exc:
        raise StoreError(f"atomic publication to {final} failed: {exc}") from exc
    return final


def cleanup_staging(staging: Path) -> None:
    """Remove a staging directory (best-effort) after a failed publication."""
    if staging.exists():
        shutil.rmtree(staging, ignore_errors=True)


__all__ = [
    "ExistingState",
    "StoreError",
    "artifact_ref",
    "cleanup_staging",
    "finalize_manifest",
    "inspect_release",
    "publish_release",
    "release_path",
    "stage_release",
    "verify_staged",
]
