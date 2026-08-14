---
title: Raster categorical to sequence adapter v1
authority: normative
document_status: draft
adapter_role: input
contract: raster-categorical-to-sequence/v1
---

# Raster categorical to sequence adapter v1

## 1. Purpose and scope

`raster-categorical-to-sequence/v1` transforms a complete categorical field over a finite rectangular task-domain position space into a categorical model-input sequence.

```text
categorical raster TaskData
        ↓
raster-categorical-to-sequence/v1
        ↓
categorical sequence ModelInput
```

The adapter owns:

- canonical position-to-slot correspondence;
- information-preserving categorical translation;
- representation-only capacity adaptation;
- construction of a target sequence mask when required solely because of representation padding;
- compatibility and derivation rules in this specification.

It does not own task scientific semantics, task targets, oracle logic, model architecture, trainable embeddings, objectives, metrics, or evaluation.

`v1` consumes an already categorical task field. Combining separate scientific roles such as passability, start, and goal into one category is outside this adapter.

## 2. Interface contract

### 2.1 Source interface

A compatible source declares:

| Requirement | Meaning |
|---|---|
| rectangular domain | finite rectangular position domain with canonical dense position identity |
| `position_count` | number `P >= 1` of source positions |
| `category[position]` | exactly one categorical identity for every canonical position |
| `source_vocabulary` | immutable identity and finite domain of source categories |

Every canonical source position is represented. `v1` has no independent source validity mask.

### 2.2 Target interface

A compatible target declares:

| Requirement | Meaning |
|---|---|
| sequence representation | categorical model-input sequence |
| `sequence_capacity` | fixed capacity `S >= 1`, or explicit variable-length support |
| `slot_identity` | stable dense slot identity |
| `target_vocabulary` | immutable identity and finite domain of accepted categories |
| `sequence_mask` | optional or required representation mask when fixed-capacity padding is present |

If the model owns trainable embeddings and accepts categorical IDs, those embeddings remain model-internal.

## 3. Transformation semantics

Canonical task positions are enumerated:

```text
p ∈ {0, ..., P-1}
```

For `v1` the position-slot correspondence is:

```text
position_to_slot(p) = p
slot_to_position(s) = s     for 0 <= s < P
```

For fixed-capacity targets with `S > P`, slots `P .. S-1` are representation-only padding and have no task-position identity.

Categories are translated by:

```text
category_mapping :
    source_vocabulary → target_vocabulary
```

The mapping must be total for every source category that may occur and injective:

```text
x != y  ⇒  category_mapping(x) != category_mapping(y)
```

so the adapter does not destroy any public categorical distinction.

When the target requires a sequence mask:

```text
sequence_mask[s] = true     for 0 <= s < P
sequence_mask[s] = false    for P <= s < S
```

The resolved position-slot correspondence is derived once and may be reused by a compatible output adapter.

## 4. Configuration and derivation

### 4.1 Authored configuration

The only `v1` authored semantic configuration is an explicit `category_mapping` when endpoint vocabulary identities do not determine the mapping uniquely.

No position count, sequence capacity, ordering, padding count, embedding dimension, or mask extent is independently authored.

### 4.2 Endpoint-owned values

| Value | Authority |
|---|---|
| rectangular domain and canonical position identity | source task-data interface |
| `P = position_count` | source task-data interface |
| source vocabulary | source task-data interface |
| target sequence capacity / variable-length support | target model-input interface |
| target slot identity | target model-input interface |
| target vocabulary | target model-input interface |
| target mask requirement | target model-input interface |

### 4.3 Derived values

Successful resolution derives:

| Value | Definition |
|---|---|
| `position_to_slot` | `p ↦ p` |
| `slot_to_position` | inverse over `0 .. P-1` |
| `represented_slots` | `0 .. P-1` |
| `padding_slots` | `P .. S-1` when `S > P` |
| `padding_count` | `S - P` for fixed capacity |
| `category_mapping` | identity or resolved authored injective mapping |
| `sequence_mask` | source-backed versus padding slots, if required |

## 5. Compatibility and resolution

Resolution succeeds only when:

1. the source exposes a finite rectangular categorical field over all canonical positions;
2. the target accepts a categorical sequence;
3. fixed target capacity satisfies `P <= S`, or the target supports variable length;
4. every possible source category has exactly one target interpretation;
5. the resolved category mapping is injective;
6. required padding can be represented by the target without assigning scientific category identity to padding;
7. no transformation requires target, oracle, privileged, or task-specific scientific information.

Successful resolution records the adapter identity/version, authored category mapping if any, derived position-slot correspondence, padding state, and compatibility evidence.

## 6. Runtime behavior

At runtime the adapter:

1. validates source data against the resolved source interface;
2. writes source position `p` to model slot `p`;
3. translates each source category through the resolved category mapping;
4. emits representation-only padding for unused fixed-capacity slots;
5. emits the derived sequence mask when required;
6. produces exactly the model-input representation established during resolution.

Runtime execution does not discover new semantic compatibility rules.

## 7. Information and semantic boundaries

The adapter may consume only the declared categorical source field and endpoint metadata required for representation.

It must not consume task targets, oracle data, privileged channels, task evaluation results, or hidden task structure.

The adapter performs representation transformation only. It does not construct scientific categories from multiple task roles, infer topology, perform model embeddings, or add learned/scientific features.

## 8. Invariants and validation

### Interface invariants

#### RIN-IF-001 — Complete source field

Every canonical source position has exactly one categorical identity.

#### RIN-IF-002 — Endpoint authority

Source domain/vocabulary and target capacity/vocabulary are consumed from their owning endpoint interfaces.

### Mapping invariants

#### RIN-MAP-001 — Canonical position-slot correspondence

Every source position `p` maps to exactly one target slot `p`.

#### RIN-MAP-002 — Information preservation

The category mapping is total and injective over all source categories that may occur.

#### RIN-MAP-003 — Padding isolation

Representation-only padding slots have no task-position or scientific category identity.

### Compatibility invariants

#### RIN-CMP-001 — Capacity

A fixed-capacity target satisfies `P <= S`.

#### RIN-CMP-002 — Vocabulary coverage

Every possible source category is representable in the target vocabulary through the resolved mapping.

### Information-boundary invariants

#### RIN-INF-001 — Public-input-only

No target, oracle, privileged, or evaluation information affects model input.

### Runtime invariants

#### RIN-RUN-001 — Resolved transformation only

Runtime performs only the transformation established during resolution.

#### RIN-RUN-002 — Target conformance

Produced model input conforms exactly to the resolved target interface.

## 9. Identity and reproducibility

Identity-bearing adapter semantics include:

- contract identity/version;
- authored category mapping when one is required.

Endpoint-owned facts and derived correspondence/padding state are recorded for reproducibility but are not independently authored adapter identity inputs when fully implied by endpoint identities and adapter configuration.

Runtime device, workers, caches, and equivalent execution concerns are not adapter semantic identity.

## 10. Failure semantics

### Resolution failures

Resolution fails for missing source/target roles, insufficient fixed capacity, incomplete or non-injective category mapping, unsupported padding representation, or any transformation requiring privileged/scientific information outside the declared source.

### Runtime contract violations

Runtime fails if actual task data violates the resolved source interface or if produced model input cannot satisfy the resolved target interface.

A failure decidable from interfaces/configuration must not be deferred to scientific execution.

## 11. Evolution

### Compatible changes

Compatible changes include non-normative clarifications, diagnostics, and optional metadata that do not alter position-slot, categorical, capacity, or information-boundary semantics.

### Breaking changes

A new version or separate adapter family is required to change canonical position-slot ordering, permit lossy categorical mapping, introduce source validity masking, construct categories from multiple scientific fields, or change padding meaning.

## 12. Examples

### Non-normative MazeHard–HRM-style composition

Suppose a task exposes a `30 × 30` categorical raster with `P = 900`, and a model accepts a categorical sequence of capacity `S = 900`.

Resolution derives:

```text
position_to_slot:
    p → p

padding_count:
    0
```

If the source and target vocabularies differ only in identity representation, an injective category mapping is resolved explicitly.

The adapter does not know that the task is MazeHard or that the model is HRM.
