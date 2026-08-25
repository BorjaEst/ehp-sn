"""Framework-controlled uncommitted logical materialization (Capability 9).

This module owns the generic boundary across which a producer hands the results
of its execution back to the framework **before** any final ``SubstrateArtifact``
publication. The substrate specifications converge on this need, and none of
them is reduced to ``list[Record]``:

* a procedural producer with intrinsic splits terminates with framework record
  identity and framework logical-resource materialization, plus producer
  descriptors;
* a complete-field producer with no split must make its domain and vocabulary
  declarations resolvable through logical resources;
* a source-import producer requires normalized topology records **and** a
  separate complete source-lineage resource;
* a retry/acceptance producer with no split delegates staging/publication to the
  framework while contributing accepted-attempt/production lineage and an
  optional region resource.

The abstraction is therefore semantically a:

.. code-block:: text

    framework-owned
    uncommitted
    logical materialization
    boundary

not merely a temporary directory. It is framework-owned (the producer cannot
publish, select a release coordinate, or commit), uncommitted (nothing produced
here appears as committed data), and logical (record bodies, descriptors, and
auxiliary resources are framework logical content, not physical files).

The session is seeded from the authoritative :class:`ExecutionPlan` so that the
producer receives exactly the resolved execution inputs — the authoritative
definition identity, output contract, opaque producer-effective configuration,
and exact bound resources — without any re-planning, re-resolution of
configuration, or independent resource reselection. The framework never
interprets producer content; the producer controls whether it executes
record-by-record, source-wide, in batches, with retries, or with deduplication.

The producer–framework handoff supported here is:

.. code-block:: text

    producer execution
            ↓
    generated record body          ← producer-owned scientific content
        + realization key          ← producer-owned canonical identity inputs
        + producer descriptors     ← e.g. intrinsic split
            ↓  (add_record)
    framework record_id derivation
            ↓
    complete logical record
            ↓
    logical record / index entry
        +
    auxiliary logical resources (lineage, domain declarations, ...)
            ↓  (add_logical_resource)
    framework logical resource set
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ehp_sn.experiments import ComponentRef
from ehp_sn.planning import ExecutionPlan, IdentityInput, ResolvedResource

from .record_identity import RealizationKey, derive_record_id


@dataclass(frozen=True, slots=True)
class GeneratedRecordBody:
    """Producer-owned scientific record content awaiting framework materialization.

    This is deliberately a **generated record body**, not a complete logical
    record: a conforming logical record also carries its framework-derived
    :attr:`~LogicalRecord.record_id`, so before the framework adds it this is not
    yet a complete conforming logical record.

    ``content`` is the producer-owned scientific payload, opaque to the
    framework. ``realization_key`` is the producer-declared canonical realization
    identity (the framework derives ``record_id`` from it). ``descriptors`` are
    additional producer-defined canonical ``(name, value)`` pairs required by the
    record's contract (for example an intrinsic split label); they are carried
    opaquely alongside the record.
    """

    content: object
    realization_key: RealizationKey
    descriptors: tuple[IdentityInput, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class LogicalRecord:
    """A complete logical record: framework ``record_id`` plus producer content.

    The framework materializes this from a :class:`GeneratedRecordBody` by
    deriving the ``record_id`` from the component identity, the output schema,
    and the producer-declared realization key. ``schema_ref`` is the authoritative
    output contract of the build, and ``descriptors`` are the producer descriptors
    carried from the generated body.
    """

    record_id: str
    schema_ref: str
    content: object
    descriptors: tuple[IdentityInput, ...]


@dataclass(frozen=True, slots=True)
class LogicalResource:
    """One auxiliary logical resource contributed by producer execution.

    Used for resources beyond per-record payloads that a concrete substrate
    requires as logical content — a complete source-lineage mapping, domain and
    vocabulary declarations, accepted-attempt production lineage, or another
    declared logical resource. ``name`` is the canonical logical resource name;
    ``content`` is framework-logical content, opaque to the framework.
    ``resource_kind`` classifies the resource (for example ``auxiliary``,
    ``lineage``) without forcing a family onto it.
    """

    name: str
    content: object
    resource_kind: str


class MaterializationSession:
    """Framework-owned uncommitted logical materialization for one build.

    Created by the framework execution orchestration, seeded from the
    authoritative :class:`ExecutionPlan`. The producer receives the session as
    its only materialization facility and populates it; it cannot select a
    release coordinate, commit, or publish. Records and auxiliary resources are
    accumulated as logical content; nothing here writes committed data.

    Producer execution may register records in any order the family requires
    (record-by-record, source-wide, after deduplication, after retries) because
    ``record_id`` is independent of registration order.
    """

    __slots__ = (
        "_component",
        "_schema_ref",
        "_configuration",
        "_resources",
        "_identity_inputs",
        "_records",
        "_logical_resources",
    )

    def __init__(
        self,
        *,
        component: ComponentRef,
        schema_ref: str,
        configuration: object,
        resources: tuple[ResolvedResource, ...],
        identity_inputs: tuple[IdentityInput, ...],
    ) -> None:
        self._component = component
        self._schema_ref = schema_ref
        self._configuration = configuration
        self._resources = resources
        self._identity_inputs = identity_inputs
        self._records: list[LogicalRecord] = []
        self._logical_resources: list[LogicalResource] = []

    @classmethod
    def from_plan(cls, plan: ExecutionPlan) -> MaterializationSession:
        """Seed a fresh session from an authoritative :class:`ExecutionPlan`.

        The plan supplies the resolved execution inputs exactly once: the
        authoritative definition identity, the output contract, the opaque
        producer-effective configuration, and the exact bound resources. The
        producer never re-resolves configuration or reselects resources.
        """
        return cls(
            component=plan.target,
            schema_ref=plan.output_contract,
            configuration=plan.configuration,
            resources=plan.resources,
            identity_inputs=plan.identity_inputs,
        )

    @property
    def component(self) -> ComponentRef:
        """The authoritative producing component reference."""
        return self._component

    @property
    def schema_ref(self) -> str:
        """The authoritative output schema the generated records conform to."""
        return self._schema_ref

    @property
    def configuration(self) -> object:
        """The opaque producer-effective configuration, exactly as planned."""
        return self._configuration

    @property
    def resources(self) -> tuple[ResolvedResource, ...]:
        """The exact bound resources, exactly as planned (never reselected)."""
        return self._resources

    @property
    def identity_inputs(self) -> tuple[IdentityInput, ...]:
        """The identity-bearing planning inputs, exactly as planned."""
        return self._identity_inputs

    @property
    def records(self) -> tuple[LogicalRecord, ...]:
        """The materialized complete logical records, in registration order."""
        return tuple(self._records)

    @property
    def logical_resources(self) -> tuple[LogicalResource, ...]:
        """The auxiliary logical resources contributed by producer execution."""
        return tuple(self._logical_resources)

    def add_record(self, body: GeneratedRecordBody) -> LogicalRecord:
        """Materialize one generated record body into a complete logical record.

        The framework derives the ``record_id`` from the producing component, the
        output schema, and the producer-declared realization key; it never reads
        the record ``content``. Returns the complete logical record so the
        producer may, if it wishes, observe the assigned identifier. Raises
        :class:`ValueError` when a duplicate ``record_id`` is registered — the
        realization key must uniquely identify one intended record.
        """
        record_id = derive_record_id(
            component_canonical=self._component.canonical,
            record_schema=self._schema_ref,
            realization_key=body.realization_key,
        )
        if any(existing.record_id == record_id for existing in self._records):
            raise ValueError(
                f"duplicate record_id {record_id!r} for component "
                f"{self._component.canonical!r}; the realization key must "
                "uniquely identify one intended record"
            )
        record = LogicalRecord(
            record_id=record_id,
            schema_ref=self._schema_ref,
            content=body.content,
            descriptors=body.descriptors,
        )
        self._records.append(record)
        return record

    def add_logical_resource(
        self,
        name: str,
        content: object,
        *,
        resource_kind: str = "auxiliary",
    ) -> LogicalResource:
        """Contribute one auxiliary logical resource to the materialization.

        ``name`` must be unique within the session; a duplicate raises
        :class:`ValueError`. ``content`` is framework-logical content, opaque to
        the framework. Returns the registered resource.
        """
        if any(existing.name == name for existing in self._logical_resources):
            raise ValueError(
                f"duplicate logical resource {name!r} in materialization for "
                f"component {self._component.canonical!r}"
            )
        resource = LogicalResource(name=name, content=content, resource_kind=resource_kind)
        self._logical_resources.append(resource)
        return resource


__all__ = [
    "GeneratedRecordBody",
    "LogicalRecord",
    "LogicalResource",
    "MaterializationSession",
]
