---
title: Content digests
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Content digests

This document defines digest semantics for EHP-SN artifacts and resources. It is the authoritative home for digest algorithms, canonical serialization, integrity verification, and the relationship between digests and identity.

## Digest algorithm and canonical serialization

Every digest defined in this document is computed as SHA-256 over the canonical serialization of its input.

Canonical serialization uses the JSON Canonicalization Scheme (JCS, RFC 8785) applied to the input's JSON-compatible representation.
This applies regardless of a resource's on-disk serialization format: a resource stored as TOML is still digested over its canonical JSON-compatible representation, not its TOML byte encoding.

## Resource digest

A resource digest is the digest of one manifest-declared resource's canonical content.
Every payload resource and the resolved-configuration resource has an individual resource digest recorded in its resource descriptor.
See [Data artifacts](data-artifacts.md) § "Resource descriptors and digests".

## Artifact fingerprint

An artifact fingerprint is the digest of the canonical identity projection for one artifact: the build-input identity fields plus every identity-bearing resource descriptor and resource digest.
It verifies the committed artifact as a whole, after payload generation.
Its exact composition and exclusions are defined by [Data artifacts](data-artifacts.md) § "Artifact fingerprint".

A resource digest and the artifact fingerprint are related but distinct: the artifact fingerprint is computed over a projection that includes resource digests as inputs, not over the same content a resource digest covers.

## Digest and identity

Digests and logical identity are distinct:

- **Logical identity** (`ArtifactRef`): durable identity used for selection and downstream inputs.
- **Resource digest** / **artifact fingerprint**: integrity/content identity of one resource, or of the committed artifact as a whole.

Equal logical identities do not imply byte-identical digests or fingerprints.
Scientific equivalence does not imply identical digests.

## Verification

Resource digests and the artifact fingerprint are verified at artifact load time.
Verification failure raises `ArtifactIntegrityError`. Verification is required before any resource is materialized from the artifact.

## Related documents

- [Identity](identity.md)
- [Artifacts](artifacts.md)
- [Manifests](manifests.md)
- [Data artifacts](data-artifacts.md)
