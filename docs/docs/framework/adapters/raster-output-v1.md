---
title: Categorical sequence to raster adapter v1
authority: normative
document_status: draft
adapter_role: output
contract: categorical-sequence-to-raster/v1
---

# Categorical sequence to raster adapter v1

## 1. Purpose and scope

`categorical-sequence-to-raster/v1` transforms a categorical model-output sequence into a categorical prediction over a rectangular task-domain position space.

```text
categorical sequence ModelOutput
        ↓
categorical-sequence-to-raster/v1
        ↓
categorical raster TaskPrediction
```

The adapter owns:

- validation and reuse of an explicit position-slot correspondence;
- categorical label translation;
- one-to-one categorical score-axis reindexing;
- removal of representation-only model slots;
- reconstruction of task-domain position order.

It does not own model-output-role selection, task scoring, oracle repair, threshold tuning, scientific validity correction, or task/model semantics.

## 2. Interface contract

### 2.1 Source interface

The selected model-output role must declare:

| Requirement | Meaning |
|---|---|
| `slot_identity` | stable dense output slot identity |
| `slot_preservation` | explicit declaration that output slots preserve the slot identity required by the resolved correspondence |
| `prediction_kind` | categorical labels or categorical scores |
| `source_vocabulary` | immutable identity and finite categorical domain |

The selected model-output role is supplied by binding/experiment composition; this adapter does not decide which scientific output role should be used.

### 2.2 Target interface

A compatible target declares:

| Requirement | Meaning |
|---|---|
| rectangular prediction domain | finite rectangular position domain |
| `position_count` | number `P >= 1` of required task prediction positions |
| `position_identity` | canonical dense task-position identity |
| `prediction_kind` | categorical labels or categorical scores |
| `target_vocabulary` | immutable identity and finite categorical domain |
| canonical score-to-label rule | only when the target explicitly requires labels derived from scores |

## 3. Transformation semantics

The adapter consumes an explicit resolved position-slot correspondence:

```text
position_to_slot : task position → model slot
slot_to_position : mapped model slot → task position
```

For the compatible `v1` raster input adapter this is:

```text
position_to_slot(p) = p
slot_to_position(s) = s
```

over source-backed slots.

The selected model-output role must explicitly preserve the model slot identity referenced by the correspondence. Equal cardinality alone is insufficient evidence.

### Categorical labels

Label adaptation uses a total deterministic:

```text
category_mapping :
    source_vocabulary → target_vocabulary
```

Many-to-one label mapping is permitted when each emitted source label has exactly one target interpretation.

### Categorical scores

Score adaptation supports only bijective correspondence between represented source and target score axes. The adapter may rename or permute axes but does not aggregate or split scores.

### Scores to labels

Score-to-label conversion occurs only when the target prediction interface explicitly declares a canonical deterministic rule supported by this adapter.

`v1` supports `argmax` only when the target explicitly requires `argmax` for mutually exclusive categorical scores.

## 4. Configuration and derivation

### 4.1 Authored configuration

The only adapter-owned semantic configuration is an explicit `category_mapping` when endpoint declarations do not determine one uniquely.

Model-output-role selection is binding/experiment configuration, not adapter-owned configuration.

No slot ordering, target position count, temporal/spatial layout, thresholds, or oracle correction is authored here.

### 4.2 Endpoint-owned values

| Value | Authority |
|---|---|
| selected source role semantics | model-output interface |
| source slot identity/preservation | model-output interface |
| source prediction kind/vocabulary | model-output interface |
| target rectangular position domain | task-prediction interface |
| target prediction kind/vocabulary | task-prediction interface |
| canonical score-to-label rule | task-prediction interface |

### 4.3 Derived values

Successful resolution validates/reuses:

| Value | Meaning |
|---|---|
| `position_to_slot` | explicit correspondence from binding composition |
| `slot_to_position` | inverse correspondence |
| `mapped_slots` | model slots with task-position identity |
| `ignored_slots` | representation-only model slots |
| `category_mapping` | resolved label mapping or score-axis bijection |

The spatial correspondence is not independently authored by this output adapter.

## 5. Compatibility and resolution

Resolution succeeds only when:

1. an explicit position-slot correspondence is available;
2. the selected source role explicitly preserves the referenced model slot identity;
3. every target position maps to exactly one source output slot;
4. categorical label mapping is total for every possible emitted source label;
5. categorical-score adaptation uses a bijective score-axis correspondence;
6. any score-to-label conversion is explicitly required by the target and supported by `v1`;
7. no transformation requires targets, oracle information, evaluation results, or scientific repair.

No unspecified "equivalent layout evidence" is accepted: the adapter requires an explicit correspondence satisfying these invariants.

## 6. Runtime behavior

At runtime the adapter:

1. validates the selected model output against the resolved source interface;
2. validates slot identity preservation;
3. ignores representation-only slots not present in the correspondence;
4. maps each task position to its corresponding model-output slot;
5. translates labels or reindexes score axes;
6. applies a score-to-label conversion only when explicitly required by the resolved target interface;
7. emits the task-domain prediction in canonical position order.

## 7. Information and semantic boundaries

The adapter may consume only the selected model prediction role, the explicit position-slot correspondence, and categorical metadata needed for mapping.

It must not consume task targets, oracle outputs, hidden task truth, evaluation results, or scientific validity information.

Representational reconstruction is permitted. Prediction repair, shortest-path correction, threshold tuning, and task scoring are not.

## 8. Invariants and validation

### Interface invariants

#### ROUT-IF-001 — Declared output role

The selected source role is explicitly declared by the model-output interface.

#### ROUT-IF-002 — Explicit slot preservation

The source role explicitly preserves the model slot identity referenced by the correspondence.

#### ROUT-IF-003 — Endpoint authority

Source and target semantic properties are consumed from their endpoint interfaces.

### Mapping invariants

#### ROUT-MAP-001 — Complete target coverage

Every target task position maps to exactly one model-output slot.

#### ROUT-MAP-002 — Total label decoding

Every possible emitted source label has exactly one target interpretation.

#### ROUT-MAP-003 — Score-axis bijection

Categorical score adaptation is bijective over represented score axes.

### Compatibility invariants

#### ROUT-CMP-001 — Explicit correspondence

Resolution requires an explicit position-slot correspondence; equal counts alone do not establish compatibility.

#### ROUT-CMP-002 — Prediction-kind compatibility

Source and target prediction kinds are directly compatible or the target explicitly declares a supported canonical score-to-label conversion.

### Information-boundary invariants

#### ROUT-INF-001 — No target/oracle dependence

Targets, oracle outputs, evaluation results, and hidden task truth do not affect adapted predictions.

### Runtime invariants

#### ROUT-RUN-001 — Resolved transformation only

Runtime performs only the transformation established during resolution.

#### ROUT-RUN-002 — Target conformance

Produced predictions conform exactly to the resolved task-prediction interface.

## 9. Identity and reproducibility

Identity-bearing adapter semantics include contract identity/version and authored category mapping when required.

The selected model-output role contributes to binding/experiment identity, not to adapter-owned configuration identity.

Endpoint-owned properties and derived spatial correspondence are recorded for reproducibility but are not independently authored adapter identity inputs.

Runtime execution concerns are not adapter semantic identity.

## 10. Failure semantics

### Resolution failures

Resolution fails for missing correspondence, missing slot-preservation guarantees, incomplete label mapping, non-bijective score-axis mapping, unsupported score-to-label conversion, incomplete target coverage, or any need for oracle/scientific repair.

### Runtime contract violations

Runtime fails when actual model output violates the resolved source interface, declared slot identity is not preserved, or produced predictions cannot satisfy the target interface.

## 11. Evolution

### Compatible changes

Compatible changes include clarifications, diagnostics, and optional metadata that do not alter correspondence, categorical mapping, prediction-kind, or information-boundary semantics.

### Breaking changes

A new version or family is required to infer correspondence from cardinality, aggregate/split score axes, introduce adapter-owned thresholds, perform scientific repair, or alter position reconstruction semantics.

## 12. Examples

### Non-normative HRM–MazeHard-style composition

Assume binding resolution already established:

```text
position 0 ↔ slot 0
...
position 899 ↔ slot 899
```

and the selected model output explicitly preserves those slot identities.

The adapter reconstructs the categorical task prediction over positions `0 .. 899`. It does not inspect the maze oracle or repair disconnected/incorrect routes.
