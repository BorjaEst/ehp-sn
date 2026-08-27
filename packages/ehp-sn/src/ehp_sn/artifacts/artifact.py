"""The durable committed ``SubstrateArtifact``.

Per the corrected lifecycle, an artifact is **committed** only when it has been
durably published at its release coordinate (``data/interim/<family>/<variant>/
v<N>/`` for the monorepo backend) and can subsequently be resolved independently
of the in-memory object that created it. The class is the durable committed form:

* it is created by publication (or reconstructed from a committed release), not
  by merely wrapping an assembled candidate in a frozen object;
* it carries the committed release coordinate, the canonical artifact reference,
  and the physical location of the committed release;
* it exposes the framework metadata (component/spec references, build-input
  identity, artifact fingerprint, declared resource descriptors, and record
  index) and logical read access to the opaque scientific content.

Distinct lifecycle states are not conflated:

```text
materialized   producer output exists but is uncommitted  (MaterializationResult)
assembled      complete immutable artifact candidate       (AssembledArtifact)
committed      candidate durably published and resolvable  (SubstrateArtifact)
```

A ``SubstrateArtifact`` is never constructed from an ``AssembledArtifact`` alone:
publication (or resolution of an existing committed release) establishes the
durable release. No physical publication implies no committed outcome.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ehp_sn.execution import LogicalRecord, LogicalResource
from ehp_sn.planning import ReleaseCoordinate

from .assembly import AssembledArtifact
from .descriptors import LogicalResourceDescriptor, ProducerDescriptor, RecordIndexEntry


@dataclass(frozen=True, slots=True)
class SubstrateArtifact:
    """A durable, committed substrate artifact at a released coordinate.

    ``assembly`` carries the framework identity metadata (build-input identity,
    artifact fingerprint) and framework-described resources plus the logical
    scientific content; ``release_coordinate`` is the committed release
    coordinate; ``artifact_ref`` is the canonical artifact reference; and
    ``location`` is the physical location of the committed release directory.

    Equality is structural, so two artifacts resolved from the same committed
    release compare equal; the immutable fields cannot change after
    construction.
    """

    assembly: AssembledArtifact
    release_coordinate: ReleaseCoordinate
    artifact_ref: str
    location: Path

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
