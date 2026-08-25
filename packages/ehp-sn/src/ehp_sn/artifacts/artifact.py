"""The committed ``SubstrateArtifact`` (logical, edition-focused).

This module defines the committed form of a substrate data artifact. Per the
"correctness of edition" scope, commitment is logical and immutable rather than
a physical publication to ``data/interim/<family>/<variant>/v<N>/``: a
``SubstrateArtifact`` is the frozen, verified description of a committed
materialization together with its logical resources for read access.

It is the **committed** counterpart of the uncommitted
:class:`~ehp_sn.execution.MaterializationResult` and of the assembled candidate
:class:`~ehp_sn.artifacts.assembly.AssembledArtifact`. A ``SubstrateArtifact``
is never constructed from a partially assembled state: it carries its final
artifact fingerprint and a lifecycle classification, so a failed or partial
build never yields an artifact that framework discovery would treat as valid
(``docs/docs/framework/artifacts.md`` § "Commitment and immutability").

This value object does not write files and does not manage a store. It is the
logical, manifest-governed access surface to a committed substrate: declared
logical resources, the record index, and the opaque scientific payloads.
"""

from __future__ import annotations

from dataclasses import dataclass

from ehp_sn.execution import LogicalRecord, LogicalResource

from .assembly import AssembledArtifact
from .descriptors import LogicalResourceDescriptor, ProducerDescriptor, RecordIndexEntry


@dataclass(frozen=True, slots=True)
class SubstrateArtifact:
    """The committed, immutable, logical substrate artifact.

    ``assembly`` carries the framework identity metadata (build-input identity,
    artifact fingerprint) and framework-described resources; ``action`` records
    the lifecycle outcome that produced this commitment (``committed`` when it
    was newly assembled and committed, ``reused`` when an equivalent verified
    artifact was returned). ``records`` and ``auxiliary`` give logical read
    access to the opaque scientific content (they are not physical payloads).

    Equality is structural, so two artifacts built from the same resolved
    materialization compare equal; the immutable fields cannot change after
    construction.
    """

    assembly: AssembledArtifact

    @property
    def component_ref(self) -> str:
        return self.assembly.component_ref

    @property
    def output_contract(self) -> str:
        return self.assembly.output_contract

    @property
    def build_input_identity(self) -> str:
        return self.assembly.build_input_identity

    @property
    def artifact_fingerprint(self) -> str:
        return self.assembly.artifact_fingerprint

    @property
    def resources(self) -> tuple[LogicalResourceDescriptor, ...]:
        return self.assembly.resources

    @property
    def index(self) -> tuple[RecordIndexEntry, ...]:
        return self.assembly.index

    @property
    def records(self) -> tuple[LogicalRecord, ...]:
        return self.assembly.records

    @property
    def auxiliary(self) -> tuple[LogicalResource, ...]:
        return self.assembly.auxiliary

    @property
    def producer_descriptors(self) -> tuple[ProducerDescriptor, ...]:
        return self.assembly.producer_descriptors

    @property
    def provenance(self) -> dict[str, object]:
        return self.assembly.provenance

    def logical_resource(self, name: str) -> LogicalResourceDescriptor | None:
        """Return the declared logical-resource descriptor ``name``, or ``None``.

        Only declared resources are openable (``manifests.md`` § "Declared
        resources"); an undeclared name returns ``None`` rather than inventing a
        resource.
        """
        for resource in self.assembly.resources:
            if resource.name == name:
                return resource
        return None

    def record(self, record_id: str) -> LogicalRecord | None:
        """Return the logical record addressed by ``record_id``, or ``None``."""
        for record in self.assembly.records:
            if record.record_id == record_id:
                return record
        return None


__all__ = ["SubstrateArtifact"]
