from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast

from ..contracts.identity import ContractRef
from ..provenance.configuration import ConfigurationEvidence
from ..provenance.production import ProductionEvidence
from .identity import ArtifactRef

ARTIFACT_MANIFEST_V1 = ContractRef(name="artifact-manifest", version=1)


@dataclass(frozen=True, slots=True, kw_only=True)
class ArtifactManifest:
    category: str
    contracts: tuple[ContractRef, ...]
    representation: str
    production: ProductionEvidence
    payload_digests: Mapping[str, str]


@dataclass(frozen=True, slots=True, kw_only=True)
class Artifact[T]:
    reference: ArtifactRef
    manifest: ArtifactManifest
    value: T


def _contract_payload(contract: ContractRef) -> dict[str, object]:
    return {"name": contract.name, "version": contract.version}


def _contract_from(payload: Mapping[str, object]) -> ContractRef:
    return ContractRef(name=cast(str, payload["name"]), version=cast(int, payload["version"]))


def _reference_payload(reference: ArtifactRef) -> dict[str, object]:
    return {"artifact_id": reference.artifact_id, "manifest_digest": reference.manifest_digest}


def manifest_to_payload(manifest: ArtifactManifest) -> dict[str, object]:
    return {
        "category": manifest.category,
        "contracts": [_contract_payload(contract) for contract in manifest.contracts],
        "representation": manifest.representation,
        "production": {
            "implementation": manifest.production.implementation,
            "source_revision": manifest.production.source_revision,
            "configuration": {
                "contract": _contract_payload(manifest.production.configuration.contract),
                "values": dict(manifest.production.configuration.values),
            },
            "inputs": {
                role: _reference_payload(reference)
                for role, reference in manifest.production.inputs.items()
            },
        },
        "payload_digests": dict(manifest.payload_digests),
    }


def manifest_to_json(manifest: ArtifactManifest) -> str:
    return json.dumps(manifest_to_payload(manifest), sort_keys=True, separators=(",", ":"))


def manifest_digest(manifest: ArtifactManifest) -> str:
    return hashlib.sha256(manifest_to_json(manifest).encode("utf-8")).hexdigest()


def manifest_from_json(text: str) -> ArtifactManifest:
    payload = json.loads(text)
    production = payload["production"]
    configuration = production["configuration"]
    return ArtifactManifest(
        category=payload["category"],
        contracts=tuple(_contract_from(item) for item in payload["contracts"]),
        representation=payload["representation"],
        production=ProductionEvidence(
            implementation=production["implementation"],
            source_revision=production["source_revision"],
            configuration=ConfigurationEvidence(
                contract=_contract_from(configuration["contract"]),
                values=configuration["values"],
            ),
            inputs={
                role: ArtifactRef(
                    artifact_id=item["artifact_id"],
                    manifest_digest=item["manifest_digest"],
                )
                for role, item in production["inputs"].items()
            },
        ),
        payload_digests=payload["payload_digests"],
    )
