---
title: Sequence to continuous raster field adapter v1
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
adapter_role: output
contract: RasterFieldPredictionAdapter
---

# Sequence to continuous raster field adapter v1

## 1. Purpose and scope

`RasterFieldPredictionAdapter` transforms one continuous-valued model-output sequence into one continuous-valued prediction field over a rectangular task-domain position space.

```text
continuous sequence ModelOutput
        ↓
RasterFieldPredictionAdapter
        ↓
continuous raster field TaskPrediction
```

The adapter owns:

- validation and reuse of an explicit position-slot correspondence;
- removal of representation-only model slots;
- reconstruction of task-domain position order.

It does not own model-output-role selection, task scoring, oracle repair, threshold tuning, scientific validity correction, value re-scaling beyond exact-range confirmation, or evaluation.

`v1` produces exactly one continuous prediction channel per adapter instance.
A task requiring several independent continuous channels (for example, distinct trajectory and waypoint fields) configures one adapter instance per channel — this adapter does not multiplex several scientific channels through one instance, matching `raster-prediction-v1`'s single-channel-per-instance precedent.

## 2. Interface contract

### 2.1 Source interface

The selected model-output role must declare:

| Requirement         | Meaning                                                                                                   |
| ------------------- | --------------------------------------------------------------------------------------------------------- |
| `slot_identity`     | stable dense output slot identity                                                                         |
| `slot_preservation` | explicit declaration that output slots preserve the slot identity required by the resolved correspondence |
| `prediction_kind`   | exactly `continuous scores`                                                                               |
| `value_range`       | immutable declared bounded numeric range (for example `[0, 1]`) every emitted value lies within           |

The selected model-output role is supplied by binding/experiment composition; this adapter does not decide which scientific output role, or which of several continuous channels, should be used.

### 2.2 Target interface

A compatible target declares:

| Requirement                   | Meaning                                                   |
| ----------------------------- | --------------------------------------------------------- |
| rectangular prediction domain | finite rectangular position domain                        |
| `position_count`              | number `P >= 1` of required task prediction positions     |
| `position_identity`           | canonical dense task-position identity                    |
| `prediction_kind`             | exactly `continuous field`                                |
| `value_range`                 | immutable declared bounded numeric range for this channel |

`v1` requires source and target `value_range` to match exactly.
The adapter does not infer a rescaling between differently declared ranges — a task and model that declare different ranges are not compatible under `v1`.

## 3. Transformation semantics

The adapter consumes an explicit resolved position-slot correspondence:

```text
position_to_slot : task position → model slot
slot_to_position : mapped model slot → task position
```

For the compatible `v1` raster overlay/sequence input adapters this is:

```text
position_to_slot(p) = p
slot_to_position(s) = s
```

over source-backed slots.

The selected model-output role must explicitly preserve the model slot identity referenced by the correspondence.
Equal cardinality alone is insufficient evidence.

Value adaptation is the identity function over the shared `value_range`:

```text
task_value(p) = model_value(position_to_slot(p))
```

No aggregation, splitting, rescaling, clipping, or thresholding is performed.

## 4. Configuration and derivation

### 4.1 Authored configuration

`v1` has no adapter-owned semantic configuration.
The spatial correspondence and value range are endpoint-owned or reused from a compatible input adapter's resolution; the selected continuous model-output role is binding/experiment configuration, not adapter-owned configuration.

No slot ordering, target position count, value transformation, thresholds, or oracle correction is authored here.

### 4.2 Endpoint-owned values

| Value                                  | Authority                 |
| -------------------------------------- | ------------------------- |
| selected source role semantics         | model-output interface    |
| source slot identity/preservation      | model-output interface    |
| source `prediction_kind`/`value_range` | model-output interface    |
| target rectangular position domain     | task-prediction interface |
| target `prediction_kind`/`value_range` | task-prediction interface |

### 4.3 Derived values

Successful resolution validates/reuses:

| Value              | Meaning                                          |
| ------------------ | ------------------------------------------------ |
| `position_to_slot` | explicit correspondence from binding composition |
| `slot_to_position` | inverse correspondence                           |
| `mapped_slots`     | model slots with task-position identity          |
| `ignored_slots`    | representation-only model slots                  |

The spatial correspondence is not independently authored by this output adapter.

## 5. Compatibility and resolution

Resolution succeeds only when:

1. an explicit position-slot correspondence is available;
2. the selected source role explicitly preserves the referenced model slot identity;
3. every target position maps to exactly one source output slot;
4. source and target `prediction_kind` are both exactly `continuous`;
5. source and target `value_range` are declared identical;
6. no transformation requires targets, oracle information, evaluation results, or scientific repair.

No unspecified "equivalent layout evidence" is accepted: the adapter requires an explicit correspondence satisfying these invariants, matching `raster-prediction-v1`'s resolution discipline.

## 6. Runtime behavior

At runtime the adapter:

1. validates the selected model output against the resolved source interface;
2. validates slot identity preservation;
3. ignores representation-only slots not present in the correspondence;
4. maps each task position to its corresponding model-output slot;
5. copies each value unchanged;
6. emits the task-domain continuous field in canonical position order.

## 7. Information and semantic boundaries

The adapter may consume only the selected model prediction role, the explicit position-slot correspondence, and range metadata needed for validation.

It must not consume task targets, oracle outputs, hidden task truth, evaluation results, or scientific validity information.

Representational reconstruction is permitted.
Prediction repair, rescaling across different declared ranges, threshold tuning, and task scoring are not.

## 8. Invariants and validation

### Interface invariants

#### RFP-IF-001 — Declared output role

The selected source role is explicitly declared by the model-output interface.

#### RFP-IF-002 — Explicit slot preservation

The source role explicitly preserves the model slot identity referenced by the correspondence.

#### RFP-IF-003 — Endpoint authority

Source and target semantic properties are consumed from their endpoint interfaces.

### Mapping invariants

#### RFP-MAP-001 — Complete target coverage

Every target task position maps to exactly one model-output slot.

#### RFP-MAP-002 — Value identity

Every mapped value is copied unchanged from source to target.

### Compatibility invariants

#### RFP-CMP-001 — Explicit correspondence

Resolution requires an explicit position-slot correspondence; equal counts alone do not establish compatibility.

#### RFP-CMP-002 — Range identity

Source and target `value_range` are declared identical; `v1` performs no cross-range rescaling.

### Information-boundary invariants

#### RFP-INF-001 — No target/oracle dependence

Targets, oracle outputs, evaluation results, and hidden task truth do not affect adapted predictions.

### Runtime invariants

#### RFP-RUN-001 — Resolved transformation only

Runtime performs only the transformation established during resolution.

#### RFP-RUN-002 — Target conformance

Produced predictions conform exactly to the resolved task-prediction interface.

## 9. Identity and reproducibility

Identity-bearing adapter semantics are limited to contract identity/version — `v1` has no authored configuration to record beyond it.

The selected model-output role contributes to binding/experiment identity, not to adapter-owned configuration identity.

Endpoint-owned properties and derived spatial correspondence are recorded for reproducibility but are not independently authored adapter identity inputs.

Runtime execution concerns are not adapter semantic identity.

## 10. Failure semantics

### Resolution failures

Resolution fails for missing correspondence, missing slot-preservation guarantees, non-`continuous` prediction kind on either side, mismatched `value_range`, incomplete target coverage, or any need for oracle/scientific repair.

### Runtime contract violations

Runtime fails when actual model output violates the resolved source interface, declared slot identity is not preserved, or produced predictions cannot satisfy the target interface.

## 11. Evolution

### Compatible changes

Compatible changes include clarifications, diagnostics, and optional metadata that do not alter correspondence, value semantics, prediction-kind, or information-boundary semantics.

### Breaking changes

A new version or family is required to infer correspondence from cardinality, support several scientific channels in one instance, perform cross-range rescaling, introduce adapter-owned thresholds, perform scientific repair, or alter position reconstruction semantics.

## 12. Examples

### Non-normative Routebind–HRM-style composition

Assume binding resolution already established:

```text
position 0 ↔ slot 0
...
position P-1 ↔ slot P-1
```

and the selected model output explicitly preserves those slot identities, declaring `prediction_kind: continuous scores` and `value_range: [0, 1]`.

The adapter reconstructs one continuous task-domain field over positions `0 .. P-1`.
A binding needing two independent fields (for example a trajectory field and a separate waypoint field) configures two independent instances of this adapter, each selecting its own model-output role.
The adapter does not inspect the route oracle or repair an implausible field value.
