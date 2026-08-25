"""Portable semantic provenance for committed data artifacts.

This module builds the framework-owned portable provenance of one committed
data artifact, applying ``docs/docs/framework/provenance.md``:

* *semantic (portable)* provenance may include the canonical field, effective
  typed value, source identity/digest, normalization/derivation rule IDs, and
  identity classification;
* *diagnostic (local)* provenance (absolute paths, token positions, original
  spelling, complete replaced values, local environment details) is deliberately
  excluded and never affects identity.

For a committed artifact, provenance records the authoritative build inputs and
bound resources without re-interpreting producer-specific configuration. The
provenance resource itself is integrity-protected but **not** identity-bearing
(it is excluded from the artifact fingerprint by default, per
``docs/docs/framework/data-artifacts.md`` § "Artifact fingerprint").
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ehp_sn.digests import canonical_digest

if TYPE_CHECKING:  # pragma: no cover - typing only
    from ehp_sn.planning import ExecutionPlan

from .identity import build_input_identity


def build_semantic_provenance(plan: ExecutionPlan) -> dict[str, object]:
    """Build the portable semantic provenance of a resolved substrate build.

    Records the authoritative build inputs and bound resources: the canonical
    component reference, the output schema, the producer-declared identity
    inputs, the exact bound resources, and the build-input identity. It does
    not reinterpret producer-specific configuration fields and carries no local
    diagnostic fields (no paths, timestamps, or hostnames).
    """
    return {
        "artifact_kind": "substrate",
        "component": plan.target.canonical,
        "output_contract": plan.output_contract,
        "identity_inputs": [{"name": item.name, "value": item.value} for item in plan.identity_inputs],
        "bound_resources": [
            {
                "requirement_ref": resource.requirement_ref,
                "resource_ref": resource.resource_ref,
                "resolution_source": resource.resolution_source,
            }
            for resource in plan.resources
        ],
        "build_input_identity": build_input_identity(plan),
    }


def provenance_resource_digest(provenance: dict[str, object]) -> str:
    """Return the integrity digest of a provenance resource (JCS of its content).

    The provenance resource is integrity-protected so its content can be
    verified, but it is not identity-bearing and does not participate in the
    artifact fingerprint.
    """
    return canonical_digest(provenance)


__all__ = ["build_semantic_provenance", "provenance_resource_digest"]
