---
title: Artifacts
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Artifacts

This document defines the artifact schema, artifact kinds, commitment semantics, and immutability guarantees for EHP-SN. It is the authoritative home for artifact behavior.

## Artifact kinds

| Kind         | Produced by           | Contains                                   |
| ------------ | --------------------- | ------------------------------------------ |
| Substrate    | `ehp-sn data build`   | Environment topology, observations, splits |
| Task corpus  | `ehp-sn tasks build`  | Task episodes, inputs, targets, splits     |
| Training run | `ehp-sn train run`    | Checkpoints, telemetry, logs, provenance   |
| Evaluation   | `ehp-sn evaluate run` | Metrics, validity records, cases, traces   |
| Analysis     | `ehp-sn analyze run`  | Tables, figures, derived resources         |
| Report       | `ehp-sn report build` | Selected outputs, presentation package     |

## Artifact identity

An artifact is identified by its `ArtifactRef` (logical identity) and verified by its artifact fingerprint. See [Identity](identity.md) and [Digests](digests.md).

`ArtifactRef`'s exact field composition is not yet specified by any document under a specification root.

## Commitment and immutability

A committed artifact is immutable. Guarantees:

- committed artifacts are not overwritten in place;
- interrupted or failed operations do not masquerade as committed artifacts;
- external tracker entries and physical directory names do not override manifest authority;
- uncommitted staging information cannot be converted directly into an `ArtifactRef`;
- result return occurs only after commitment succeeds.

## Reuse

An equivalent verified artifact may be reused when its manifest and identity fingerprint match. Reuse does not modify provenance and returns the existing logical reference.

## Related documents

- [Manifests](manifests.md)
- [Digests](digests.md)
- [Identity](identity.md)
- [Checkpoints](checkpoints.md)
- [Provenance](provenance.md)
