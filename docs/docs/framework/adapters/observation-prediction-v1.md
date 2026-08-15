---
title: Sensory-prediction sequence to observation sequence adapter v1
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
adapter_role: output
contract: ObservationPredictionAdapter
---

# Sensory-prediction sequence to observation sequence adapter v1

## 1. Purpose and scope

`ObservationPredictionAdapter` transforms an aligned model-native sequence of categorical sensory predictions into an aligned task-domain sequence of categorical observation predictions.

```text
sensory-prediction ModelOutput
        ↓
ObservationPredictionAdapter
        ↓
observation TaskPrediction
```

The adapter owns:

- validation and reuse of an explicit task-step/model-step correspondence;
- categorical label translation;
- one-to-one score-axis reindexing;
- removal of representation-only model steps;
- task-domain prediction reconstruction.

It does not own model-output-role selection, scientific preference between prediction pathways, task scoring, revisit semantics, temporal shifting, threshold tuning, calibration, oracle repair, or model trace interpretation.

## 2. Interface contract

### 2.1 Source interface

The selected model-output role must declare:

| Requirement               | Meaning                                                                                    |
| ------------------------- | ------------------------------------------------------------------------------------------ |
| `model_step_identity`     | stable dense output-step identity                                                          |
| `step_preservation`       | explicit preservation of the model-step identity referenced by the resolved correspondence |
| `prediction_kind`         | categorical labels or categorical scores                                                   |
| `source_vocabulary`       | immutable identity and finite sensory-prediction domain                                    |
| `prediction_timing`       | explicit model-owned timing identity for the selected prediction                           |
| `prediction_conditioning` | explicit model-owned description/identity of the information conditioning that prediction  |

Latent structural state, conjunctive state, recurrent state, memory diagnostics, and traces are not prediction roles unless the model explicitly declares them as such.

The selected source role is supplied by binding/experiment composition.

### 2.2 Target interface

A compatible target declares:

| Requirement                   | Meaning                                                        |
| ----------------------------- | -------------------------------------------------------------- |
| `step_count`                  | number `T >= 1` of required task prediction steps              |
| `task_step_identity`          | stable dense task-prediction identity                          |
| `prediction_kind`             | categorical labels or categorical scores                       |
| `target_vocabulary`           | immutable identity and finite observation-prediction domain    |
| `prediction_timing`           | explicit task-owned timing identity required of the prediction |
| canonical score-to-label rule | only when the target requires labels derived from scores       |

`v1` requires source and target `prediction_timing` identities to match exactly. The adapter does not infer semantic equivalence between differently declared timing/conditioning regimes.

## 3. Transformation semantics

The adapter consumes an explicit task-step/model-step correspondence:

```text
task_step_to_model_step : task step → model step
model_step_to_task_step : mapped model step → task step
```

For the compatible `v1` sequence input adapter:

```text
task_step_to_model_step(t) = t
model_step_to_task_step(u) = u
```

The selected model-output role must explicitly preserve those model-step identities. Equal sequence lengths are insufficient evidence.

No temporal shift is performed.

### Categorical labels

Label adaptation uses a total deterministic:

```text
category_mapping :
    source_vocabulary → target_vocabulary
```

Many-to-one label mapping is permitted when each emitted source label has exactly one target interpretation.

### Categorical scores

Score adaptation requires a bijection between represented source and target score axes. The adapter may rename or permute axes but does not aggregate or split scores.

### Scores to labels

Score-to-label conversion occurs only when the target explicitly declares a canonical deterministic conversion supported by this adapter.

`v1` supports `argmax` only when the target explicitly requires `argmax`.

## 4. Configuration and derivation

### 4.1 Authored configuration

The only adapter-owned semantic configuration is an explicit `category_mapping` when endpoint declarations do not determine one uniquely.

The selected model prediction role is binding/experiment configuration, not adapter-owned configuration.

There is no authored temporal offset, task/model sequence length, threshold, calibration rule, revisit-conditioned decision, or oracle correction.

### 4.2 Endpoint-owned values

| Value                                 | Authority                 |
| ------------------------------------- | ------------------------- |
| selected prediction-role semantics    | model-output interface    |
| model-step identity/preservation      | model-output interface    |
| source prediction timing/conditioning | model-output interface    |
| source prediction kind/vocabulary     | model-output interface    |
| task prediction step domain           | task-prediction interface |
| target prediction timing              | task-prediction interface |
| target prediction kind/vocabulary     | task-prediction interface |
| canonical score-to-label rule         | task-prediction interface |

### 4.3 Derived values

Successful resolution validates/reuses:

| Value                     | Meaning                                          |
| ------------------------- | ------------------------------------------------ |
| `task_step_to_model_step` | explicit correspondence from binding composition |
| `model_step_to_task_step` | inverse correspondence                           |
| `mapped_model_steps`      | model steps with task-prediction identity        |
| `ignored_model_steps`     | representation-only steps                        |
| `category_mapping`        | resolved label mapping or score-axis bijection   |

No temporal alignment is independently authored by this output adapter.

## 5. Compatibility and resolution

Resolution succeeds only when:

1. an explicit task-step/model-step correspondence is available;
2. the selected source role is explicitly declared as a categorical sensory prediction;
3. the selected source role preserves the model-step identity referenced by the correspondence;
4. every required task prediction step maps to exactly one model-output step;
5. source and target `prediction_timing` identities match exactly;
6. categorical label mapping is total for every possible emitted source label;
7. categorical-score adaptation uses a bijective score-axis correspondence;
8. any score-to-label conversion is explicitly required by the target and supported by `v1`;
9. no temporal shift is required;
10. no transformation depends on targets, revisit truth, oracle information, evaluation results, or scientific repair.

The adapter does not infer compatibility from task/model identity or from informal similarity between prediction-conditioning descriptions.

## 6. Runtime behavior

At runtime the adapter:

1. validates the selected model output against the resolved source interface;
2. validates model-step identity preservation;
3. ignores representation-only model steps not present in the correspondence;
4. maps each required task step to its corresponding model-output step;
5. translates labels or reindexes score axes;
6. applies a score-to-label conversion only when explicitly required by the target;
7. emits the task-domain observation-prediction sequence.

It does not evaluate correctness, revisit status, memory quality, or scientific validity.

## 7. Information and semantic boundaries

The adapter may consume only the selected declared prediction role, explicit step correspondence, and endpoint categorical/timing metadata needed for mapping.

It must not consume task targets, revisit truth, physical positions, complete topology, oracle outputs, evaluation results, or hidden task truth.

It must not reinterpret latent structural/conjunctive states, memory values, recurrent state, or diagnostic traces as predictions unless the model-output interface explicitly declares them as the selected prediction role.

Representational decoding is permitted. Scientific interpretation and correction are not.

## 8. Invariants and validation

### Interface invariants

#### SOUT-IF-001 — Declared prediction role

The selected source role is explicitly declared by the model-output interface as a categorical sensory prediction.

#### SOUT-IF-002 — Explicit step preservation

The selected source role explicitly preserves the model-step identity referenced by the correspondence.

#### SOUT-IF-003 — Explicit timing

Source and target prediction timing identities are explicit.

#### SOUT-IF-004 — Endpoint authority

Endpoint-owned output, timing, sequence, and vocabulary semantics are not independently configured by the adapter.

### Mapping invariants

#### SOUT-MAP-001 — Complete target coverage

Every required task prediction step maps to exactly one model-output step.

#### SOUT-MAP-002 — No temporal shift

`v1` performs no temporal shift.

#### SOUT-MAP-003 — Total label decoding

Every possible emitted source label has exactly one target interpretation.

#### SOUT-MAP-004 — Score-axis bijection

Categorical score adaptation is bijective over represented score axes.

### Compatibility invariants

#### SOUT-CMP-001 — Explicit correspondence

An explicit task-step/model-step correspondence is required; equal lengths alone do not establish compatibility.

#### SOUT-CMP-002 — Timing identity

Source and target prediction-timing identities match exactly in `v1`.

#### SOUT-CMP-003 — Prediction-kind compatibility

Source and target kinds are directly compatible or the target explicitly declares a supported canonical score-to-label conversion.

### Information-boundary invariants

#### SOUT-INF-001 — No target/oracle dependence

Targets, revisit truth, oracle outputs, evaluation results, and privileged task information do not affect adapted predictions.

#### SOUT-INF-002 — No latent reinterpretation

Model latent states/traces are not promoted to task predictions unless explicitly declared as the selected prediction role.

### Runtime invariants

#### SOUT-RUN-001 — Resolved transformation only

Runtime performs only the transformation established during resolution.

#### SOUT-RUN-002 — Target conformance

Produced task predictions conform exactly to the resolved target interface.

## 9. Identity and reproducibility

Identity-bearing adapter semantics include contract identity/version and authored category mapping when required.

The selected model-output role contributes to binding/experiment identity, not adapter-owned configuration identity.

Endpoint-owned prediction/timing semantics and derived step correspondence are recorded for reproducibility but are not independently authored adapter identity inputs.

Runtime execution concerns are not adapter semantic identity.

## 10. Failure semantics

### Resolution failures

Resolution fails for missing correspondence, undeclared prediction roles, missing step-preservation guarantees, mismatched prediction-timing identity, incomplete label mapping, non-bijective score-axis mapping, unsupported score-to-label conversion, incomplete target coverage, required temporal shifts, or any need for target/oracle/scientific repair.

### Runtime contract violations

Runtime fails when actual model output violates the resolved source interface, model-step identity is not preserved, or produced predictions cannot satisfy the target interface.

## 11. Evolution

### Compatible changes

Compatible changes include clarifications, diagnostics, and optional metadata that do not alter step correspondence, timing, categorical mapping, prediction-kind, or information-boundary semantics.

### Breaking changes

A new version or family is required for temporal shifts, non-identical timing compatibility, score aggregation/splitting, adapter-owned thresholds, reinterpretation of model traces, or scientific repair.

## 12. Examples

### Non-normative TEM–Arena-style composition

Assume binding/experiment composition selects a declared TEM-like sensory-prediction role whose:

```text
prediction_timing = current_step
model_step_identity = preserved
```

and the Arena-like target requires:

```text
prediction_timing = current_step
```

The adapter reuses the resolved task-step/model-step correspondence and maps sensory prediction categories back to observation categories.

It does not use physical position or revisit truth and does not decide whether another model prediction pathway would be scientifically preferable.
