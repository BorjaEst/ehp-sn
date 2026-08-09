---
title: Checkpoints
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Checkpoints

This document defines checkpoint identity, capability levels, and resume/initialization semantics. It is the authoritative home for checkpoint behavior.

## Checkpoint identity

A `CheckpointRef` resolves:

- parent training-run `ArtifactRef`;
- checkpoint `ResourceRef`;
- checkpoint role and selection metadata where declared;
- experiment, model, corpus, lineage, and step metadata.

A checkpoint location is not a portable checkpoint identity. Only committed checkpoint resources are valid downstream references.

## Capability levels

| Capability            | Meaning                                                                                  |
| --------------------- | ---------------------------------------------------------------------------------------- |
| `resumable`           | Contains model, optimizer, scheduler, step, and protocol state for training continuation |
| `initialization-only` | Contains model parameters for starting a new training lineage                            |
| `inference-only`      | Contains model parameters sufficient for evaluation                                      |

## Resume and initialization

- `resume` continues the same training lineage. Requires a `resumable` checkpoint.
- `init_from` starts a new training lineage. Accepts `initialization-only` or `resumable` checkpoints.
- They are mutually exclusive.
- Resume validates parent run identity, committed checkpoint resource, resolved experiment digest, corpus identity, model structure, optimizer compatibility, and completed-step history.

Only checkpoints committed before an interruption are resumable.

## Related documents

- [Artifacts](artifacts.md)
- [Manifests](manifests.md)
- [Identity](identity.md)
