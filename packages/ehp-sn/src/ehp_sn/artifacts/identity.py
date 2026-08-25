"""Build-input identity and artifact fingerprint for data artifacts.

This module applies the framework-wide digest mechanism
(``ehp_sn.digests``) to the data-artifact identity semantics of
``docs/docs/framework/data-artifacts.md`` § "Build-input identity" and
§ "Artifact fingerprint", together with ``docs/docs/framework/identity.md``.

Three identities remain deliberately distinct:

```text
PlanId            -> one authoritative plan (ehp_sn.planning.plan_identity)
build-input        -> resolved identity-affecting inputs, computed before
   identity           payload generation (which scientific build this is)
artifact           -> committed artifact as a whole, computed after
   fingerprint        generation (identity projection + identity-bearing
                      resource digests)
record_id          -> one logical record (ehp_sn.execution.derive_record_id)
```

Per the "correctness of edition" scope, release-number allocation and physical
coordinates are deliberately out of scope: identity is computed from resolved
semantic inputs only, never from release numbers, physical paths, or audit
fields (``data-artifacts.md`` § "Artifact fingerprint" exclusions).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ehp_sn.digests import canonical_digest

if TYPE_CHECKING:  # pragma: no cover - typing only
    from ehp_sn.planning import ExecutionPlan

from .descriptors import LogicalResourceDescriptor

#: The artifact kind this lifecycle assembles.
_ARTIFACT_KIND = "substrate"


def build_input_identity(plan: ExecutionPlan) -> str:
    """Return the build-input identity of a resolved substrate build.

    Derived from the resolved identity-affecting inputs (the artifact kind, the
    canonical substrate reference, the output/shared schema, the canonical
    producer-declared identity-bearing inputs, and the exact bound resources).
    It does not include output resource digests (those do not exist before
    generation) and is deliberately independent of release numbers and physical
    coordinates. Equal resolved inputs yield an equal build-input identity via
    the exact JCS mechanism (``ehp_sn.digests``).
    """
    return canonical_digest(
        {
            "artifact_kind": _ARTIFACT_KIND,
            "component": plan.target.canonical,
            "output_contract": plan.output_contract,
            "resources": [
                {
                    "requirement_ref": resource.requirement_ref,
                    "resource_ref": resource.resource_ref,
                    "resolution_source": resource.resolution_source,
                }
                for resource in plan.resources
            ],
            "identity_inputs": [
                {"name": item.name, "value": item.value} for item in plan.identity_inputs
            ],
        }
    )


def artifact_fingerprint(
    build_input_identity: str,
    resources: tuple[LogicalResourceDescriptor, ...],
) -> str:
    """Return the artifact fingerprint over a canonical identity projection.

    The projection includes the build-input identity and every identity-bearing
    logical resource's descriptor fields and digest. It excludes:
    non-identity-bearing resource descriptors (for example provenance), the
    fingerprint field itself, timestamps, hostnames, absolute paths, physical
    storage locations, and other audit-only fields.

    The digest uses the exact JCS mechanism; it is not computable before payload
    generation because the identity-bearing resource digests are only known
    after materialization.
    """
    projection = {
        "build_input_identity": build_input_identity,
        "resources": [
            {
                "name": resource.name,
                "resource_kind": resource.resource_kind,
                "schema_ref": resource.schema_ref,
                "split": resource.split,
                "digest": resource.digest,
            }
            for resource in resources
            if resource.identity_bearing
        ],
    }
    return canonical_digest(projection)


__all__ = ["artifact_fingerprint", "build_input_identity"]
