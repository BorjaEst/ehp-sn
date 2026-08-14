---
title: Observation-relation sequence to sensory-relation sequence adapter v1
authority: normative
document_status: draft
adapter_role: input
contract: observation-relation-sequence-to-sensory-relation-sequence/v1
---

# Observation-relation sequence to sensory-relation sequence adapter v1

## 1. Purpose and scope

`observation-relation-sequence-to-sensory-relation-sequence/v1` transforms an ordered task sequence of categorical observations and incoming relations into an aligned model-input sequence of categorical sensory and relation identities.

```text
observation/relation TaskData
        ↓
observation-relation-sequence-to-sensory-relation-sequence/v1
        ↓
sensory/relation ModelInput
```

The adapter owns:

- task-step-to-model-step correspondence;
- information-preserving observation-to-sensory translation;
- information-preserving ordinary-relation translation;
- translation of sequence-start semantics into the target reset/init representation;
- representation-only sequence padding;
- compatibility and derivation rules in this specification.

It does not own task episode semantics, revisit truth, physical position, model embeddings, recurrent dynamics, latent states, memory, prediction semantics, objectives, traces, or evaluation.

`v1` represents one task episode/segment per adapted sequence. Step `0` is the sequence start. Packed multiple-episode sequences require another contract or explicit higher-level batching semantics.

## 2. Interface contract

### 2.1 Source interface

A compatible source declares:

| Requirement | Meaning |
|---|---|
| `step_count` | number `T >= 1` of task steps |
| `step_identity` | stable dense task-step identity `0 .. T-1` |
| `observation[step]` | one public categorical observation identity per step |
| `observation_vocabulary` | immutable identity and finite observation domain |
| `relation[step]` | categorical incoming relation for each ordinary step `t > 0` |
| `relation_vocabulary` | immutable identity and finite ordinary relation domain |
| `relation_alignment` | explicit declaration that `relation[t]` denotes the transition into `observation[t]` |
| sequence start | step `0` is explicitly the episode/segment start |

No ordinary scientific relation is required at step `0`.

Targets, revisit truth, physical positions, complete topology, and privileged/oracle channels are outside the source interface.

### 2.2 Target interface

A compatible target declares:

| Requirement | Meaning |
|---|---|
| sequence representation | aligned sensory/relation model-input sequence |
| `sequence_capacity` | fixed `S >= 1`, or explicit variable-length support |
| `model_step_identity` | stable dense model-step identity |
| `sensory_vocabulary` | immutable identity and finite sensory domain |
| `model_relation_vocabulary` | immutable identity and finite ordinary relation domain |
| `relation_alignment` | incoming-relation alignment |
| reset/init representation | explicit model-native representation for sequence start |
| `sequence_mask` | optional or required representation mask for fixed-capacity padding |

If the model owns trainable sensory/relation embeddings, the adapter outputs IDs rather than embeddings.

## 3. Transformation semantics

For source steps:

```text
t ∈ {0, ..., T-1}
```

`v1` preserves step identity:

```text
task_step_to_model_step(t) = t
model_step_to_task_step(u) = u     for 0 <= u < T
```

No temporal shift or look-ahead insertion is permitted.

Observations use a total injective mapping:

```text
observation_mapping :
    observation_vocabulary → sensory_vocabulary
```

Ordinary relations use a total injective mapping:

```text
relation_mapping :
    relation_vocabulary → model_relation_vocabulary
```

At task step `0`, the adapter emits the target-declared reset/init representation. It does not fabricate an ordinary scientific relation.

For fixed capacity `S > T`, model steps `T .. S-1` are representation-only padding. If a target mask is required:

```text
sequence_mask[u] = true     for 0 <= u < T
sequence_mask[u] = false    for T <= u < S
```

The resolved step correspondence is derived once and may be reused by a compatible output adapter.

## 4. Configuration and derivation

### 4.1 Authored configuration

The adapter may author only:

| Configuration | Meaning |
|---|---|
| `observation_mapping` | source observation → target sensory identity |
| `relation_mapping` | source ordinary relation → target ordinary relation identity |

These mappings are required only when endpoint declarations do not determine them uniquely.

There is no authored step count, sequence capacity, temporal offset, reset placement, padding count, or embedding dimension.

### 4.2 Endpoint-owned values

| Value | Authority |
|---|---|
| task step domain and `T` | source task-data interface |
| observation vocabulary | source task-data interface |
| ordinary relation vocabulary/alignment | source task-data interface |
| sequence-start semantics | source task-data interface |
| target capacity/variable-length support | target model-input interface |
| model-step identity | target model-input interface |
| sensory/relation vocabularies | target model-input interface |
| target reset/init representation | target model-input interface |
| target mask requirement | target model-input interface |

### 4.3 Derived values

Successful resolution derives:

| Value | Definition |
|---|---|
| `task_step_to_model_step` | `t ↦ t` |
| `model_step_to_task_step` | inverse over `0 .. T-1` |
| `represented_steps` | `0 .. T-1` |
| `padding_steps` | `T .. S-1` when `S > T` |
| `padding_count` | `S - T` for fixed capacity |
| `observation_mapping` | identity or resolved authored injective mapping |
| `relation_mapping` | identity or resolved authored injective mapping |
| `reset_mapping` | source sequence start → target reset/init representation |
| `sequence_mask` | represented versus padding model steps when required |

## 5. Compatibility and resolution

Resolution succeeds only when:

1. source task steps are finite and densely ordered;
2. every task step has exactly one public observation;
3. source and target both declare incoming-relation alignment;
4. step `0` can be represented using the target reset/init mechanism;
5. fixed capacity satisfies `T <= S`, or the target supports variable length;
6. observation mapping is total and injective;
7. ordinary-relation mapping is total and injective;
8. no temporal shift is required;
9. adaptation needs no target, revisit, position, oracle, or privileged information.

Successful resolution records adapter identity/version, authored mappings, derived step correspondence, reset mapping, padding state, and compatibility evidence.

## 6. Runtime behavior

At runtime the adapter:

1. validates the task sequence against the resolved source interface;
2. preserves step order exactly;
3. maps each observation through the resolved observation mapping;
4. emits target reset/init at model step `0`;
5. maps each ordinary incoming relation for steps `t > 0`;
6. pads unused fixed-capacity model steps when required;
7. emits the derived sequence mask when required;
8. produces exactly the resolved model-input representation.

## 7. Information and semantic boundaries

The adapter may consume only public observation identities, ordinary relation identities, sequence-start semantics, and declared step structure.

It must not consume targets, revisit truth, physical positions, full topology, oracle outputs, privileged channels, future observations to construct current input, or evaluation results.

It does not infer structural state, create TEM-like latent variables, perform memory retrieval, or construct trainable embeddings unless the target interface itself declares embedded vectors as its native input.

## 8. Invariants and validation

### Interface invariants

#### SIN-IF-001 — Complete observation sequence

Every task step has exactly one public observation identity.

#### SIN-IF-002 — Explicit incoming-relation semantics

Source and target explicitly declare incoming-relation alignment.

#### SIN-IF-003 — Explicit reset semantics

Sequence start and target reset/init semantics are explicit and are not encoded by silently reusing an ordinary scientific relation.

#### SIN-IF-004 — Endpoint authority

Endpoint-owned sequence, vocabulary, capacity, and reset semantics are not independently configured by the adapter.

### Mapping invariants

#### SIN-MAP-001 — Step preservation

Every task step maps to the model step with the same dense identity.

#### SIN-MAP-002 — Observation information preservation

Observation mapping is total and injective.

#### SIN-MAP-003 — Relation information preservation

Ordinary-relation mapping is total and injective.

#### SIN-MAP-004 — Padding isolation

Representation-only padding has no task-step, observation, or scientific relation identity.

### Compatibility invariants

#### SIN-CMP-001 — Capacity

A fixed-capacity target satisfies `T <= S`.

#### SIN-CMP-002 — Reset representability

The target explicitly supports the source sequence-start condition.

#### SIN-CMP-003 — Alignment

Source and target relation alignment declarations match exactly in `v1`.

### Information-boundary invariants

#### SIN-INF-001 — Public-input-only

No target, revisit, position, oracle, privileged, or evaluation information affects model input.

#### SIN-INF-002 — No future leakage

Model input at task step `t` is not constructed from observations at later task steps.

### Runtime invariants

#### SIN-RUN-001 — Resolved transformation only

Runtime performs only the transformation established during resolution.

#### SIN-RUN-002 — Target conformance

Produced model input conforms exactly to the resolved target interface.

## 9. Identity and reproducibility

Identity-bearing adapter semantics include contract identity/version and authored observation/relation mappings when required.

Endpoint-owned facts and derived step/reset/padding state are recorded for reproducibility but are not independently authored adapter identity inputs.

Runtime execution concerns are not adapter semantic identity.

## 10. Failure semantics

### Resolution failures

Resolution fails for missing sequence roles, incompatible relation alignment, unrepresentable reset/init semantics, insufficient capacity, incomplete/non-injective mappings, required temporal shifts, or any need for privileged/target information.

### Runtime contract violations

Runtime fails when actual task data violates the resolved source interface or the produced model input cannot satisfy the resolved target interface.

## 11. Evolution

### Compatible changes

Compatible changes include clarifications, diagnostics, and optional metadata that do not alter step alignment, mapping, reset, padding, or information-boundary semantics.

### Breaking changes

A new version or family is required for temporal shifts, multiple episode starts inside one adapted sequence, lossy observation/relation mappings, different reset semantics, scientific feature inference, or use of future context.

## 12. Examples

### Non-normative Arena–TEM-style composition

```text
step:          0      1      2      3
observation:   o7     o3     o8     o7
incoming rel.: —      east   north  west
```

The adapter preserves steps `0..3`, translates observation and ordinary-relation identities, and emits the model's reset/init representation at step `0`.

Physical positions, revisit labels, and full environment topology are not model inputs through this adapter.
