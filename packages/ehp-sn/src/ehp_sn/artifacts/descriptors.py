"""Framework logical-resource and record-index descriptors for data artifacts.

This module defines the framework-owned descriptors that describe the logical
resources and records of a materialized data artifact (``docs/docs/framework/
data-artifacts.md`` § "Resource descriptors and digests" and
``docs/docs/framework/contracts/index.md`` § "Minimal enumerated record
contract"). They are the *representation* of manifest-declared resources and
record-index entries; they are not physical files and not an artifact store.

Three descriptor shapes mirror three distinct concerns:

* :class:`LogicalResourceDescriptor` — one manifest-declared logical resource
  (payload / resolved-configuration / auxiliary), its schema reference, its
  identity-bearing and split status, and its canonical content digest;
* :class:`RecordIndexEntry` — one logical record's addressable entry:
  ``record_id``, ``schema_ref``, a ``payload_locator``, and producer-required
  index descriptors;
* :class:`ProducerDescriptor` — one opaque producer-declared descriptor (for
  example an intrinsic split label or a variant) carried alongside the record
  or the artifact without the framework interpreting it.

Nothing here branches on a substrate family or interprets a producer field
(``ARCH-001``); the descriptors are generic framework logical content.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class LogicalResourceDescriptor:
    """One manifest-declared logical resource of a data artifact.

    ``name`` is the canonical logical resource name (for example
    ``manifest``, ``config.resolved``, ``provenance``, ``index``, or a
    producer-declared payload/auxiliary resource). ``schema_ref`` is the schema
    the resource conforms to where applicable. ``resource_kind`` classifies the
    resource (``payload``, ``resolved-config``, ``provenance``, ``index``,
    ``auxiliary``, ...) without forcing a family onto it.

    ``identity_bearing`` marks whether the resource participates in the
    artifact fingerprint: payload resources and the resolved configuration are
    identity-bearing by default; audit resources (provenance) are not.
    ``split`` is an optional intrinsic split association (``None`` when the
    artifact or resource has no split). ``digest`` is the resource digest
    computed over the resource's canonical logical content; it is ``None``
    until computed.
    """

    name: str
    resource_kind: str
    schema_ref: str | None = None
    identity_bearing: bool = True
    split: str | None = None
    digest: str | None = None


@dataclass(frozen=True, slots=True)
class ProducerDescriptor:
    """One opaque producer-declared canonical descriptor.

    This is the framework *representation* of a producer-defined (name, value)
    pair — for example an intrinsic split label, a variant, or a lineage role —
    that the framework carries opaquely and never interprets by name or value.
    """

    name: str
    value: Any


@dataclass(frozen=True, slots=True)
class RecordIndexEntry:
    """One record's addressable entry in the artifact record index.

    Mirrors the minimal enumerated record contract of
    ``docs/docs/framework/contracts/index.md``: ``record_id``, ``schema_ref``,
    a ``payload_locator``, and producer-required index descriptors. The
    ``payload_locator`` is the logical reference by which the record's payload
    is resolved within the artifact (a logical resource + logical record key),
    not a physical path.
    """

    record_id: str
    schema_ref: str
    payload_locator: str
    descriptors: tuple[ProducerDescriptor, ...] = field(default_factory=tuple)


__all__ = ["LogicalResourceDescriptor", "ProducerDescriptor", "RecordIndexEntry"]
