"""Plan identity: the plan-specific application of the framework digest.

This module owns the composition of the canonical plan-identity projection
(``docs/docs/framework/identity.md`` § "PlanId"): it derives the stable
framework ``PlanId`` of an :class:`ExecutionPlan` by projecting its
identity-bearing content and digesting it with the framework-wide mechanism
(``ehp_sn.digests.canonical_digest``).

The digest *mechanism* itself (exact RFC 8785 canonical serialization + SHA-256)
is framework-wide and lives in ``ehp_sn.digests``; planning is only one of its
consumers, alongside record identity (``ehp_sn.execution``) and later artifact
fingerprints. Nothing here redefines the algorithm.

Plan identity is deliberately **not** artifact identity: the artifact
fingerprint is defined separately in ``docs/docs/framework/data-artifacts.md``
and is not computable before generation. :func:`plan_identity` only provides the
stable identity by which a validation report (and later lifecycle stage) can
refer to one authoritative plan without re-serializing it.
"""

from __future__ import annotations

from ehp_sn.digests import canonical_digest

from .plan import ExecutionPlan


def plan_identity(plan: ExecutionPlan) -> str:
    """Return the stable framework identity of an :class:`ExecutionPlan`.

    The plan identity is derived from the plan's identity-bearing content: its
    selected target, its authoritative output contract, its exact bound
    resources, and its producer-declared identity inputs. Two plans built from
    the same resolved components and scientific inputs yield the same identity;
    a different identity-bearing input yields a different identity.

    It does **not** include any output resource digest (those do not exist
    before generation) and is distinct from the committed artifact fingerprint
    (``docs/docs/framework/data-artifacts.md`` § "Artifact fingerprint").
    """
    return canonical_digest(
        {
            "target": plan.target.canonical,
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


__all__ = ["plan_identity"]
