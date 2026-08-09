---
title: Provenance
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Provenance

This document defines the separation between portable semantic provenance and local diagnostic provenance. It is the authoritative home for provenance schema and identity contribution rules.

## Portable vs diagnostic provenance

### Semantic provenance (portable)

Portable provenance may include:

- canonical field;
- effective typed value;
- source class;
- source document identity or digest;
- document-relative locator;
- normalization rule ID;
- derivation rule ID;
- identity classification.

### Diagnostic provenance (local)

Diagnostic provenance is local and non-portable. It may include:

- absolute filesystem path;
- CLI token position;
- original textual spelling;
- complete replaced values;
- local environment details.

Diagnostic provenance must not affect scientific or operational identity.

## Workspace provenance

The full workspace digest is diagnostic provenance only. The effective workspace projection contains only consumed defaults and bindings. The effective projection's digest, not the full workspace digest, may contribute to operational identity.

## Provenance in artifacts

Every committed artifact records both semantic and diagnostic provenance.
Portable provenance is recorded as one declared provenance resource; the manifest records only its resource digest, not its content, per [Data artifacts](data-artifacts.md) § "Manifest, configuration, and provenance authority".
Diagnostic provenance is recorded outside the manifest-tracked resource set and is not required for artifact verification or reuse.

## Related documents

- [Identity](identity.md)
- [Artifacts](artifacts.md)
- [Manifests](manifests.md)
