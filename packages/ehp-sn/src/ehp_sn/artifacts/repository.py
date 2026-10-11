from __future__ import annotations

import os
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from ..contracts.validation import ContractValidator
from ..provenance.production import ProductionEvidence
from .codec import ArtifactCodec
from .errors import (
    ArtifactIntegrityError,
    InvalidArtifact,
    UnsupportedRepresentation,
)
from .identity import ArtifactRef
from .integrity import ArtifactIntegrity
from .manifest import (
    Artifact,
    ArtifactManifest,
    manifest_digest,
    manifest_from_json,
    manifest_to_json,
)


class ArtifactRepository(Protocol):
    def describe(self, reference: ArtifactRef) -> ArtifactManifest: ...

    def publish[T](
        self,
        value: T,
        *,
        codec: ArtifactCodec[T],
        validators: Sequence[ContractValidator],
        production: ProductionEvidence,
    ) -> ArtifactRef: ...

    def load[T](
        self,
        reference: ArtifactRef,
        *,
        codec: ArtifactCodec[T],
        validators: Sequence[ContractValidator] = (),
    ) -> Artifact[T]: ...


class LocalArtifactRepository:
    def __init__(self, root: Path) -> None:
        self._root = Path(root)
        self._manifests = self._root / "manifests"
        self._payloads = self._root / "payloads"
        self._integrity = ArtifactIntegrity()

    def describe(self, reference: ArtifactRef) -> ArtifactManifest:
        path = self._manifests / f"{reference.manifest_digest}.json"
        if not path.is_file():
            raise InvalidArtifact("manifest is not present in the repository", reference=reference)
        manifest = manifest_from_json(path.read_text(encoding="utf-8"))
        if manifest_digest(manifest) != reference.manifest_digest:
            raise ArtifactIntegrityError(
                "manifest digest does not match its reference", reference=reference
            )
        return manifest

    def publish[T](
        self,
        value: T,
        *,
        codec: ArtifactCodec[T],
        validators: Sequence[ContractValidator],
        production: ProductionEvidence,
    ) -> ArtifactRef:
        for validator in validators:
            validator.validate(value)

        self._manifests.mkdir(parents=True, exist_ok=True)
        self._payloads.mkdir(parents=True, exist_ok=True)

        payload_digest = self._store_payload(value, codec)
        manifest = ArtifactManifest(
            category=codec.category(),
            contracts=tuple(codec.contracts()),
            representation=codec.representation(),
            production=production,
            payload_digests={"payload": payload_digest},
        )
        artifact_id = manifest_digest(manifest)
        manifest_path = self._manifests / f"{artifact_id}.json"
        if not manifest_path.is_file():
            _atomic_write(manifest_path, manifest_to_json(manifest))
        return ArtifactRef(artifact_id=artifact_id, manifest_digest=artifact_id)

    def load[T](
        self,
        reference: ArtifactRef,
        *,
        codec: ArtifactCodec[T],
        validators: Sequence[ContractValidator] = (),
    ) -> Artifact[T]:
        manifest = self.describe(reference)
        if manifest.representation != codec.representation():
            raise UnsupportedRepresentation(
                f"unsupported representation {manifest.representation!r}",
                representation=manifest.representation,
            )
        declared = set(manifest.contracts)
        for contract in codec.contracts():
            if contract not in declared:
                raise InvalidArtifact(
                    f"manifest does not declare contract {contract.name!r}", reference=reference
                )
        digest = manifest.payload_digests.get("payload")
        if digest is None:
            raise InvalidArtifact("manifest declares no payload", reference=reference)
        blob = self._payloads / digest
        if not blob.is_file():
            raise ArtifactIntegrityError("payload is not present in the repository", reference=reference)
        self._integrity.verify(blob, digest)
        value = codec.read(blob, manifest)
        for validator in validators:
            validator.validate(value)
        return Artifact(reference=reference, manifest=manifest, value=value)

    def _store_payload[T](self, value: T, codec: ArtifactCodec[T]) -> str:
        staging = Path(tempfile.mkdtemp(prefix=".staging-", dir=self._root))
        try:
            staged = staging / "payload"
            codec.write(value, staged)
            digest = self._integrity.digest(staged)
            blob = self._payloads / digest
            if blob.exists():
                staged.unlink()
            else:
                os.replace(staged, blob)
            return digest
        finally:
            if staging.exists():
                staging.rmdir()


def _atomic_write(path: Path, text: str) -> None:
    descriptor, name = tempfile.mkstemp(dir=path.parent, prefix=".tmp-", suffix=".json")
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
