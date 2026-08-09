---
title: Artifact manifests
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Artifact manifests

This document defines the structure and authority of EHP-SN artifact manifests. It is the authoritative home for manifest schema, declared resources, and manifest authority.

## Manifest authority

The manifest is the authoritative scientific record of a completed operation. It is the single source of truth for:

- artifact identity and artifact fingerprint;
- scientific inputs and their identities;
- resolved request and plan identities;
- portable execution provenance;
- declared resources and their identities;
- schema version;
- commitment status.

External tracker entries, physical directory names, and filesystem metadata do not override manifest authority.

## Declared resources

A manifest declares the resources owned by the artifact. Only manifest-declared resources can be opened.
Resource references remain linked to their owning artifact identity.

## Manifest validation

Manifest integrity is verified at artifact load time. Schema and integrity checks occur before any resource is materialized.
Missing or corrupt declared resources raise `ResourceError` or `ArtifactIntegrityError`.

## Related documents

- [Artifacts](artifacts.md)
- [Digests](digests.md)
- [Identity](identity.md)
- [Provenance](provenance.md)
