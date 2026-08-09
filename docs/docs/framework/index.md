---
title: Framework reference
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Framework reference

The framework reference defines the authoritative semantics for EHP-SN's core infrastructure: identity, references, artifacts, manifests, digests, checkpoints, and provenance.

These documents are the single authoritative home for each concept. Other documentation — particularly the configuration interface — references them rather than duplicating their definitions.

## Dependency order

```text
component and resource references
    → compatibility
    → digests and identity
    → artifact and manifest semantics
    → checkpoint semantics
    → provenance
    → configuration identity contribution
    → request and plan resolution
```

## Documents

| Document                          | Owns                                                                     |
| --------------------------------- | ------------------------------------------------------------------------ |
| [References](references.md)       | Canonical reference grammar, version semantics, resource reference kinds |
| [Compatibility](compatibility.md) | Component compatibility declarations, support levels, maturity           |
| [Identity](identity.md)           | Identity categories, scientific vs operational identity, identity inputs |
| [Digests](digests.md)             | Content digest semantics, algorithms, integrity verification             |
| [Artifacts](artifacts.md)         | Artifact schema, artifact kinds, commitment, immutability                |
| [Manifests](manifests.md)         | Manifest structure, declared resources, manifest authority               |
| [Checkpoints](checkpoints.md)     | Checkpoint identity, capability levels, resume and initialization        |
| [Provenance](provenance.md)       | Portable vs diagnostic provenance, provenance schema                     |

## Terminology

**Normative:** establishes requirements that conforming implementations or documents must satisfy.

**Canonical:** designates the normalized, preferred, or uniquely designated representation of an entity.
A canonical representation is not necessarily the document that authoritatively defines it.

For example, the reference grammar in [References](references.md) is normative, while `task:arena/v1` is the canonical string representation produced under that grammar.
