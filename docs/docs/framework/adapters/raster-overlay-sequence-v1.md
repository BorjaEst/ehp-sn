---
title: Raster multi-channel overlay to sequence adapter v1
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
adapter_role: input
contract: RasterOverlaySequenceAdapter
---

# Raster multi-channel overlay to sequence adapter v1

## 1. Purpose and scope

`RasterOverlaySequenceAdapter` transforms several simultaneous declared categorical or binary channels over one finite rectangular task-domain position space into one categorical model-input sequence.

```text
N categorical/binary raster channels (TaskData)
        ↓
RasterOverlaySequenceAdapter
        ↓
categorical sequence ModelInput
```

The adapter owns:

- canonical position-to-slot correspondence;
- deterministic, information-preserving combination of `N` declared per-position channel values into one combined per-slot categorical identity;
- representation-only capacity adaptation;
- construction of a target sequence mask when required solely because of representation padding;
- compatibility and derivation rules in this specification.

It does not own task scientific semantics, task targets, oracle logic, model architecture, trainable embeddings, objectives, metrics, or evaluation, and it does not decide which channels a task publishes as public input — that selection is task-owned.

`v1` consumes `N >= 1` already-categorical or binary task channels declared public by the source task-data interface. It combines their values into one representational category per position; it does not infer, derive, or invent a new scientific category not already implied by the declared channel values.

This is the generalization `raster-sequence-v1.md` §1 explicitly excludes: "Combining separate scientific roles such as passability, start, and goal into one category is outside this adapter." `RasterOverlaySequenceAdapter` is that combination, made generic and information-preserving rather than task-specific.

## 2. Interface contract

### 2.1 Source interface

A compatible source declares:

| Requirement             | Meaning                                                                                          |
| ----------------------- | ------------------------------------------------------------------------------------------------ |
| rectangular domain      | finite rectangular position domain with canonical dense position identity                        |
| `position_count`        | number `P >= 1` of source positions                                                              |
| `channel_count`         | number `N >= 1` of declared public channels                                                      |
| `channel_vocabulary[i]` | immutable identity and finite domain of channel `i`'s categorical/binary values                  |
| `channel[i][position]`  | exactly one value of `channel_vocabulary[i]` for every canonical position, for every channel `i` |

Every canonical source position is represented by every declared channel. `v1` has no independent source validity mask.

Targets, oracle data, privileged channels, and any channel not declared public by the source task-data interface are outside the source interface.

### 2.2 Target interface

A compatible target declares:

| Requirement             | Meaning                                                                         |
| ----------------------- | ------------------------------------------------------------------------------- |
| sequence representation | categorical model-input sequence                                                |
| `sequence_capacity`     | fixed capacity `S >= 1`, or explicit variable-length support                    |
| `slot_identity`         | stable dense slot identity                                                      |
| `target_vocabulary`     | immutable identity and finite domain of accepted categories                     |
| `sequence_mask`         | optional or required representation mask when fixed-capacity padding is present |

Identical to `raster-sequence-v1.md` §2.2 — this adapter targets the same class of model-input sequence interface; only the source side differs.

## 3. Transformation semantics

Canonical task positions are enumerated `p ∈ {0, ..., P-1}`. As in `raster-sequence-v1`, the position-slot correspondence is the identity:

```text
position_to_slot(p) = p
slot_to_position(s) = s     for 0 <= s < P
```

For each position `p`, the adapter reads the declared channel tuple

```text
channel_tuple(p) = (channel[0][p], channel[1][p], ..., channel[N-1][p])
```

and translates it through a total, injective combination mapping

```text
channel_combination_mapping :
    channel_vocabulary[0] × ... × channel_vocabulary[N-1] → target_vocabulary
```

The mapping is total over every channel-tuple combination that may occur across the declared source channels, and injective:

```text
channel_tuple(p) != channel_tuple(q)  ⇒  channel_combination_mapping(channel_tuple(p)) != channel_combination_mapping(channel_tuple(q))
```

so the adapter does not collapse any distinction any individual channel makes, and does not lose one channel's distinction in favor of another's.

For fixed-capacity targets with `S > P`, slots `P .. S-1` are representation-only padding and have no task-position identity, identical to `raster-sequence-v1.md` §3.

When the target requires a sequence mask, it is derived identically to `raster-sequence-v1.md` §3.

## 4. Configuration and derivation

### 4.1 Authored configuration

The only `v1` authored semantic configuration is the explicit `channel_combination_mapping`, when the declared channel vocabularies do not determine a combination uniquely. This is a genuine representational choice — how to combine `N` independent, task-owned categorical distinctions into one representational slot — that neither endpoint alone determines, analogous to `raster-sequence-v1.md`'s single-channel `category_mapping` but over a channel tuple rather than one channel.

No position count, sequence capacity, ordering, padding count, channel count, channel vocabulary, embedding dimension, or mask extent is independently authored. In particular, `channel_count` and each `channel_vocabulary[i]` are endpoint-owned (declared by the source task-data interface); the adapter does not decide how many channels exist or what any one channel's values mean.

### 4.2 Endpoint-owned values

| Value                                              | Authority                    |
| -------------------------------------------------- | ---------------------------- |
| rectangular domain and canonical position identity | source task-data interface   |
| `P = position_count`                               | source task-data interface   |
| `N = channel_count`                                | source task-data interface   |
| each `channel_vocabulary[i]`                       | source task-data interface   |
| target sequence capacity / variable-length support | target model-input interface |
| target slot identity                               | target model-input interface |
| target vocabulary                                  | target model-input interface |
| target mask requirement                            | target model-input interface |

### 4.3 Derived values

Successful resolution derives:

| Value                         | Definition                                              |
| ----------------------------- | ------------------------------------------------------- |
| `position_to_slot`            | `p ↦ p`                                                 |
| `slot_to_position`            | inverse over `0 .. P-1`                                 |
| `represented_slots`           | `0 .. P-1`                                              |
| `padding_slots`               | `P .. S-1` when `S > P`                                 |
| `padding_count`               | `S - P` for fixed capacity                              |
| `channel_combination_mapping` | identity-implied or resolved authored injective mapping |
| `sequence_mask`               | source-backed versus padding slots, if required         |

## 5. Compatibility and resolution

Resolution succeeds only when:

1. the source exposes `N >= 1` finite rectangular categorical/binary channels, each covering every canonical position;
2. the target accepts a categorical sequence;
3. fixed target capacity satisfies `P <= S`, or the target supports variable length;
4. every possible channel-tuple combination has exactly one target interpretation;
5. the resolved combination mapping is injective over the declared channel-tuple space;
6. required padding can be represented by the target without assigning scientific category identity to padding;
7. no transformation requires target, oracle, privileged, or task-specific scientific information beyond the declared public channels.

Successful resolution records the adapter identity/version, authored combination mapping if any, derived position-slot correspondence, padding state, and compatibility evidence.

## 6. Runtime behavior

At runtime the adapter:

1. validates source data against the resolved source interface;
2. writes source position `p` to model slot `p`;
3. reads the declared channel tuple at `p` and translates it through the resolved combination mapping;
4. emits representation-only padding for unused fixed-capacity slots;
5. emits the derived sequence mask when required;
6. produces exactly the model-input representation established during resolution.

Runtime execution does not discover new semantic compatibility rules.

## 7. Information and semantic boundaries

The adapter may consume only the declared public categorical/binary channels and endpoint metadata required for representation.

It must not consume task targets, oracle data, privileged channels, task evaluation results, or hidden task structure — including any channel the source task-data interface does not declare public.

The adapter performs representation transformation only. It does not construct new scientific categories beyond the declared channel tuple, infer topology, perform model embeddings, or add learned/scientific features. Combining `N` declared channels into one representational slot is representation-only exactly because the combination is total and injective (§3) — no channel's distinction is created, inferred, or discarded.

## 8. Invariants and validation

### Interface invariants

#### ROV-IF-001 — Complete source channels

Every canonical source position has exactly one value for every declared channel.

#### ROV-IF-002 — Endpoint authority

Source domain/channel vocabularies and target capacity/vocabulary are consumed from their owning endpoint interfaces.

### Mapping invariants

#### ROV-MAP-001 — Canonical position-slot correspondence

Every source position `p` maps to exactly one target slot `p`.

#### ROV-MAP-002 — Information preservation

The channel-combination mapping is total and injective over the declared channel-tuple space.

#### ROV-MAP-003 — Padding isolation

Representation-only padding slots have no task-position or scientific category identity.

### Compatibility invariants

#### ROV-CMP-001 — Capacity

A fixed-capacity target satisfies `P <= S`.

#### ROV-CMP-002 — Vocabulary coverage

Every possible declared channel-tuple combination is representable in the target vocabulary through the resolved mapping.

### Information-boundary invariants

#### ROV-INF-001 — Public-input-only

No target, oracle, privileged, or evaluation information affects model input.

### Runtime invariants

#### ROV-RUN-001 — Resolved transformation only

Runtime performs only the transformation established during resolution.

#### ROV-RUN-002 — Target conformance

Produced model input conforms exactly to the resolved target interface.

## 9. Identity and reproducibility

Identity-bearing adapter semantics include:

- contract identity/version;
- authored channel-combination mapping when one is required.

Endpoint-owned facts and derived correspondence/padding state are recorded for reproducibility but are not independently authored adapter identity inputs when fully implied by endpoint identities and adapter configuration.

Runtime device, workers, caches, and equivalent execution concerns are not adapter semantic identity.

## 10. Failure semantics

### Resolution failures

Resolution fails for missing source/target roles, insufficient fixed capacity, incomplete or non-injective combination mapping, unsupported padding representation, or any transformation requiring privileged/scientific information outside the declared public channels.

### Runtime contract violations

Runtime fails if actual task data violates the resolved source interface or if produced model input cannot satisfy the resolved target interface.

A failure decidable from interfaces/configuration must not be deferred to scientific execution.

## 11. Evolution

### Compatible changes

Compatible changes include non-normative clarifications, diagnostics, and optional metadata that do not alter position-slot, channel-combination, capacity, or information-boundary semantics.

### Breaking changes

A new version or separate adapter family is required to change canonical position-slot ordering, permit lossy channel combination, introduce source validity masking, infer a channel not declared by the source, or change padding meaning.

## 12. Examples

### Non-normative Routebind–HRM-style composition

Suppose a task publicly declares four channels over a `P`-position rectangular domain: traversability (`wall`/`free`), observation identity (cardinality `K`), a unique-start binary channel, and a goal-observation-support binary channel — and a model accepts a categorical sequence of capacity `S = P`.

Resolution derives:

```text
position_to_slot:
    p → p

padding_count:
    0

channel_combination_mapping:
    (traversability, observation, start, goal-support) → combined_category
```

The combined-category vocabulary has cardinality bounded by the product of the four channel cardinalities; the resolved mapping need only cover tuples that actually occur.

The adapter does not know that the task is Routebind or that the model is HRM.
