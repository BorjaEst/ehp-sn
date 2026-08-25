"""Generic artifact assembly: framework metadata describing a materialized substrate.

This module owns the framework-owned step that turns the uncommitted
:class:`~ehp_sn.execution.MaterializationResult` (its authoritative plan and
populated materialization session) into an assembled candidate artifact —
framework metadata that describes **what** was materialized without publishing
it and without invoking the producer again.

Per ``docs/docs/framework/data-artifacts.md``, assembly establishes:

```text
artifact kind = substrate
component/spec identity
output/shared schema
logical resource descriptors
producer descriptors
provenance
framework identity metadata (build-input identity, artifact fingerprint)
```

The critical invariant: *artifact assembly knows WHAT was materialized, not HOW
the producer generated it.* Assembly consumes the authoritative plan (it never
reloads configuration) and the plan-bound materialization (it never invokes
producer execution). Producer-specific scientific content remains opaque; it
contributes to the fingerprint only through canonical logical-resource digests.

Logical resources support both ordinary record payloads and non-record
auxiliary resources. There is no requirement of one logical resource per record
nor one physical file per logical resource, and no serialization format is
fixed (content digests are computed over the exact JCS canonical representation
of logical content, per ``docs/docs/framework/digests.md``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ehp_sn.digests import canonical_digest
from ehp_sn.execution import LogicalRecord, LogicalResource, MaterializationResult

from .descriptors import LogicalResourceDescriptor, ProducerDescriptor, RecordIndexEntry
from .identity import artifact_fingerprint, build_input_identity
from .provenance import build_semantic_provenance, provenance_resource_digest

if TYPE_CHECKING:  # pragma: no cover - typing only
    from ehp_sn.planning import ExecutionPlan

#: Canonical logical names of the framework-declared resources.
_PAYLOADS_RESOURCE = "payloads"
_INDEX_RESOURCE = "index"
_RESOLVED_CONFIG_RESOURCE = "resolved-config"
_PROVENANCE_RESOURCE = "provenance"


@dataclass(frozen=True, slots=True)
class AssembledArtifact:
    """The assembled candidate: framework metadata for an uncommitted substrate.

    This is deliberately **not** a ``SubstrateArtifact`` and not a partial one:
    it is the framework-owned description of the materialized logical content
    that a later commit step closes into a committed artifact. It carries:

    * ``component_ref`` / ``output_contract`` — the authoritative producing
      component and shared output schema;
    * ``build_input_identity`` — from the resolved plan, before generation;
    * ``resources`` — the identity-bearing and audit logical-resource
      descriptors with their canonical digests;
    * ``index`` — the record index entries with framework ``record_id``s;
    * ``records`` / ``auxiliary`` — the logical scientific content (opaque to
      the framework) for access after commit;
    * ``producer_descriptors`` — the artifact-level producer-declared
      descriptor surface, from producer output (never from config inspection);
    * ``provenance`` and its digest — the portable semantic provenance;
    * ``artifact_fingerprint`` — the committed-artifact identity projection
      computed from ``build_input_identity`` plus identity-bearing resource
      digests.
    """

    component_ref: str
    output_contract: str
    build_input_identity: str
    resources: tuple[LogicalResourceDescriptor, ...]
    index: tuple[RecordIndexEntry, ...]
    records: tuple[LogicalRecord, ...]
    auxiliary: tuple[LogicalResource, ...]
    producer_descriptors: tuple[ProducerDescriptor, ...]
    provenance: dict[str, object]
    provenance_digest: str
    artifact_fingerprint: str


def _payloads_digest(records: tuple[LogicalRecord, ...]) -> str:
    """Digest of the ordered record payloads (by record_id, then registration).

    Computed over the exact JCS canonical representation of each record's
    scientific content plus its schema and producer descriptors — never an ad
    hoc Python serialization (``data-artifacts.md`` / ``digests.md``).
    """
    return canonical_digest(
        [
            {
                "record_id": record.record_id,
                "schema_ref": record.schema_ref,
                "descriptors": [{"name": d.name, "value": d.value} for d in record.descriptors],
                "content": record.content,
            }
            for record in records
        ]
    )


def _resolved_config_digest(plan: ExecutionPlan) -> str:
    """Digest of the framework-visible resolved configuration representation.

    The producer's opaque configuration object is not inspected; its resolved
    identity-bearing semantics are already declared by the producer as canonical
    identity inputs on the plan. This digest covers that framework-visible
    resolved representation so the resolved-config resource is identity-bearing
    and verifiable without the framework reading producer fields.
    """
    return canonical_digest(
        {
            "identity_inputs": [
                {"name": item.name, "value": item.value} for item in plan.identity_inputs
            ],
            "resources": [
                {
                    "requirement_ref": resource.requirement_ref,
                    "resource_ref": resource.resource_ref,
                    "resolution_source": resource.resolution_source,
                }
                for resource in plan.resources
            ],
        }
    )


def assemble_artifact(
    plan: ExecutionPlan,
    result: MaterializationResult,
) -> AssembledArtifact:
    """Assemble framework metadata for an uncommitted substrate materialization.

    Consumes the authoritative ``ExecutionPlan`` (produced exactly once) and the
    plan-bound :class:`MaterializationResult` produced from that same plan. It
    never reloads configuration, never invokes producer execution, and never
    inspects a producer configuration type. Producer scientific content stays
    opaque and contributes to identity only through canonical logical-resource
    digests.
    """
    records: tuple[LogicalRecord, ...] = result.materialization.records
    auxiliary: tuple[LogicalResource, ...] = result.materialization.logical_resources

    build_input = build_input_identity(plan)

    # --- record index ---
    index = tuple(
        RecordIndexEntry(
            record_id=record.record_id,
            schema_ref=record.schema_ref,
            payload_locator=f"{_PAYLOADS_RESOURCE}:{record.record_id}",
            descriptors=tuple(
                ProducerDescriptor(name=d.name, value=d.value) for d in record.descriptors
            ),
        )
        for record in records
    )

    # --- logical resource descriptors ---
    payloads_digest = _payloads_digest(records)
    config_digest = _resolved_config_digest(plan)
    index_digest = canonical_digest(
        [
            {
                "record_id": entry.record_id,
                "schema_ref": entry.schema_ref,
                "payload_locator": entry.payload_locator,
            }
            for entry in index
        ]
    )
    resource_descriptors: list[LogicalResourceDescriptor] = [
        LogicalResourceDescriptor(
            name=_PAYLOADS_RESOURCE,
            resource_kind="payload",
            schema_ref=plan.output_contract,
            identity_bearing=True,
            digest=payloads_digest,
        ),
        LogicalResourceDescriptor(
            name=_RESOLVED_CONFIG_RESOURCE,
            resource_kind="resolved-config",
            schema_ref=None,
            identity_bearing=True,
            digest=config_digest,
        ),
        LogicalResourceDescriptor(
            name=_INDEX_RESOURCE,
            resource_kind="index",
            schema_ref=None,
            identity_bearing=False,
            digest=index_digest,
        ),
    ]
    for resource in auxiliary:
        resource_descriptors.append(
            LogicalResourceDescriptor(
                name=resource.name,
                resource_kind=resource.resource_kind,
                schema_ref=None,
                identity_bearing=True,
                digest=canonical_digest(resource.content),
            )
        )

    # --- provenance (audit resource, not identity-bearing) ---
    provenance = build_semantic_provenance(plan)
    provenance_digest = provenance_resource_digest(provenance)
    resource_descriptors.append(
        LogicalResourceDescriptor(
            name=_PROVENANCE_RESOURCE,
            resource_kind="provenance",
            schema_ref=None,
            identity_bearing=False,
            digest=provenance_digest,
        )
    )

    # --- artifact-level producer descriptors (aggregated from producer output) ---
    producer_descriptors = _aggregate_producer_descriptors(records)

    # --- artifact fingerprint ---
    fingerprint = artifact_fingerprint(build_input, tuple(resource_descriptors))

    return AssembledArtifact(
        component_ref=plan.target.canonical,
        output_contract=plan.output_contract,
        build_input_identity=build_input,
        resources=tuple(resource_descriptors),
        index=index,
        records=records,
        auxiliary=auxiliary,
        producer_descriptors=producer_descriptors,
        provenance=provenance,
        provenance_digest=provenance_digest,
        artifact_fingerprint=fingerprint,
    )


def _aggregate_producer_descriptors(
    records: tuple[LogicalRecord, ...],
) -> tuple[ProducerDescriptor, ...]:
    """Aggregate the distinct producer-declared descriptor surface of the artifact.

    Collected from producer output (record descriptors), not from inspecting
    configuration types. Each distinct descriptor name is represented once with
    its producer-declared values, preserving deterministic (name-sorted) order.
    """
    seen: dict[str, set[object]] = {}
    for record in records:
        for descriptor in record.descriptors:
            seen.setdefault(descriptor.name, set()).add(descriptor.value)
    return tuple(
        ProducerDescriptor(name=name, value=sorted(values, key=lambda v: str(v)))
        for name, values in sorted(seen.items())
    )
